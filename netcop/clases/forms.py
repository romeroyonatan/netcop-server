import re
import os
import uuid
from . import models
from django import forms
from django.conf import settings


REGEX_CIDR = ("^\s*(?P<ip>((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
              "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
              "(/(?P<prefijo>\d+))?\s*$")
REGEX_PUERTO = "^\s*(?P<numero>\d+)(/(?P<protocolo>(tcp|udp)))?\s*$"

PUERTO_MIN = 1
PUERTO_MAX = 65535
PREFIJO_MIN = 0
PREFIJO_MAX = 32


class ClaseForm(forms.ModelForm):
    '''
    Formulario para agilizar la creación de clases de trafico.
    '''

    class Meta:
        model = models.ClaseTrafico
        fields = '__all__'

    subredes_outside = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""Lista de redes en Internet (separadas por nueva linea) con
        el formato <strong>direccion/prefijo</strong> donde la direccion es el
        identificador de red y el prefijo es la cantidad de bits que contiene
        la máscara de subred. Si no se ingresa un prefijo, se entiende que se
        trata de una dirección de host.""",
    )
    puertos_outside = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""Lista de puertos en Internet (separados por nueva linea)
        con el formato <strong>numero/protocolo</strong> donde el numero es el
        identificador del puerto y el protocolo puede ser 'tcp' o 'udp'. Si no
        se especifica protocolo, se asume que el puerto puede pertenecer a
        cualquiera de ellos.""",
    )
    subredes_inside = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""Lista de redes en la red local (separadas por nueva linea)
        con el formato <strong>direccion/prefijo</strong> donde la direccion es
        el identificador de red y el prefijo es la cantidad de bits que
        contiene la máscara de subred. Si no se ingresa un prefijo, se entiende
        que se trata de una dirección de host.""",
    )
    puertos_inside = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""Lista de puertos en la red local (separados por nueva
        linea) con el formato <strong>numero/protocolo</strong> donde el numero
        es el identificador del puerto y el protocolo puede ser 'tcp' o 'udp'.
        Si no se especifica protocolo, se asume que el puerto puede pertenecer
        a cualquiera de ellos.""",
    )

    def __init__(self, *args, **kwargs):
        r = super().__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance')
            redes_outside = [
                str(item.cidr) for item in instance
                                           .redes
                                           .filter(grupo=models.OUTSIDE)
                                           .order_by('cidr__direccion')
            ]
            redes_inside = [
                str(item.cidr) for item in instance
                                           .redes
                                           .filter(grupo=models.INSIDE)
                                           .order_by('cidr__direccion')
            ]
            puertos_outside = [
                str(item.puerto) for item in instance
                                             .puertos
                                             .filter(grupo=models.OUTSIDE)
                                             .order_by('puerto__numero')
            ]
            puertos_inside = [
                str(item.puerto) for item in instance
                                             .puertos
                                             .filter(grupo=models.INSIDE)
                                             .order_by('puerto__numero')
            ]
            self.initial["subredes_outside"] = "\n".join(redes_outside)
            self.initial["subredes_inside"] = "\n".join(redes_inside)
            self.initial["puertos_outside"] = "\n".join(puertos_outside)
            self.initial["puertos_inside"] = "\n".join(puertos_inside)
        return r

    def save(self, *args, **kwargs):
        clase = super().save(*args, **kwargs)
        self.actualizar_colecciones(clase, self.cleaned_data)
        self.calcular_version()
        return clase

    def actualizar_colecciones(self, clase, campos):
        '''
        Actualiza las listas de subredes y puertos de la clase de trafico.
        '''
        redes = (('subredes_outside', models.OUTSIDE),
                 ('subredes_inside', models.INSIDE))
        puertos = (('puertos_outside', models.OUTSIDE),
                   ('puertos_inside', models.INSIDE))

        # borro antiguas relaciones
        models.ClaseCIDR.objects.filter(clase=clase).delete()
        models.ClasePuerto.objects.filter(clase=clase).delete()

        # creo las nuevas relaciones
        for nombre, grupo in redes:
            string = campos.get(nombre, "")
            for cidr in self.obtener_cidr(string):
                clase.redes.create(clase=clase, cidr=cidr, grupo=grupo)

        for nombre, grupo in puertos:
            string = campos.get(nombre, "")
            for puerto in self.obtener_puertos(string):
                clase.puertos.create(clase=clase, puerto=puerto, grupo=grupo)

    def obtener_cidr(self, string):
        '''
        Parsea y devuelve las cidr que contenga el string pasado por parametro.
        '''
        p = re.compile(REGEX_CIDR, flags=re.M)
        for m in p.finditer(string):
            direccion = m.groupdict().get('ip')
            prefijo = m.groupdict().get('prefijo') or 32
            yield models.CIDR.objects.get_or_create(
                direccion=direccion, prefijo=int(prefijo))[0]

    def obtener_puertos(self, string):
        '''
        Parsea y devuelve los puertos que contenga el string pasado por
        parametro.
        '''
        p = re.compile(REGEX_PUERTO, flags=re.I | re.M)
        for m in p.finditer(string):
            numero = m.groupdict().get('numero')
            protocolo = m.groupdict().get('protocolo') or ''
            protocolo = self.obtener_numero(protocolo)
            yield models.Puerto.objects.get_or_create(
                numero=int(numero), protocolo=protocolo)[0]

    def obtener_numero(self, string):
        '''
        Obtiene el numero de protocolo en base a una cadena de caracteres.
        Retornos
        ---------------
          * 6 - TCP | tcp
          * 17 - UDP | udp
          * 0 en cualquier otro caso.
        '''
        if string.lower() == 'tcp':
            return 6
        elif string.lower() == 'udp':
            return 17
        return 0

    def clean_subredes_outside(self):
        '''
        Metodo ejecutado al validar el campo subredes_outside.
        '''
        data = self.cleaned_data["subredes_outside"]
        if data:
            self.validar_subredes(data)
        return data

    def clean_subredes_inside(self):
        '''
        Metodo ejecutado al validar el campo subredes_inside.
        '''
        data = self.cleaned_data["subredes_inside"]
        if data:
            self.validar_subredes(data)
        return data

    def clean_puertos_outside(self):
        '''
        Metodo ejecutado al validar el campo puertos_outside.
        '''
        data = self.cleaned_data["puertos_outside"]
        if data:
            self.validar_puertos(data)
        return data

    def clean_puertos_inside(self):
        '''
        Metodo ejecutado al validar el campo puertos_inside.
        '''
        data = self.cleaned_data["puertos_inside"]
        if data:
            self.validar_puertos(data)
        return data

    def validar_subredes(self, string):
        '''
        Valida que cada subred ingresada sea correcta.
        '''
        p = re.compile(REGEX_CIDR)
        for line in string.splitlines():
            line = line.strip()
            if line:
                m = p.match(line)
                if m is None:
                    raise forms.ValidationError("%s: Error de sintaxis" % line)
                direccion = m.groupdict().get('ip')
                prefijo = m.groupdict().get('prefijo') or 32
                if not PREFIJO_MIN <= int(prefijo) <= PREFIJO_MAX:
                    raise forms.ValidationError(
                        "%s: El prefijo debe ser entre %d y %d" %
                        (direccion, PREFIJO_MIN, PREFIJO_MAX)
                    )

    def validar_puertos(self, string):
        '''
        Valida que cada puerto ingresado sea correcto.
        '''
        p = re.compile(REGEX_PUERTO, flags=re.I)
        for line in string.splitlines():
            line = line.strip()
            if line:
                m = p.match(line)
                if m is None:
                    raise forms.ValidationError("%s: Error de sintaxis" % line)
                numero = m.groupdict().get('numero')
                if not PUERTO_MIN <= int(numero) <= PUERTO_MAX:
                    raise forms.ValidationError(
                        "%s: el número de puerto debe ser entre %d y %d" %
                        (numero, PUERTO_MIN, PUERTO_MAX)
                    )

    def calcular_version(self):
        '''
        Calcula el nuevo numero de version y lo guarda en un archivo para
        proximas consultas.
        '''
        path = os.path.join(settings.MEDIA_ROOT, 'version')
        with open(path, 'w') as f:
            f.write(uuid.uuid4().hex)
