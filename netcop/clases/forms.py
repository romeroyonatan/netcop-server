import re
from . import models
from django import forms

REGEX_CIDR = ("(?P<ip>((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
              "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
              "(/(?P<prefijo>\d+))?")
REGEX_PUERTO = "(?P<numero>\d+)(/(?P<protocolo>(tcp|udp)))?"


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
            redes_outside = [str(item.cidr) for item in
                             instance.redes.filter(grupo=models.OUTSIDE)]
            redes_inside = [str(item.cidr) for item in
                            instance.redes.filter(grupo=models.INSIDE)]
            puertos_outside = [str(item.puerto) for item in
                               instance.puertos.filter(grupo=models.OUTSIDE)]
            puertos_inside = [str(item.puerto) for item in
                              instance.puertos.filter(grupo=models.INSIDE)]
            self.initial["subredes_outside"] = "\n".join(redes_outside)
            self.initial["subredes_inside"] = "\n".join(redes_inside)
            self.initial["puertos_outside"] = "\n".join(puertos_outside)
            self.initial["puertos_inside"] = "\n".join(puertos_inside)
        return r

    def save(self, *args, **kwargs):
        clase = super().save(*args, **kwargs)
        self.actualizar_colecciones(clase, self.cleaned_data)
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
            yield models.CIDR.objects.get_or_create(direccion=direccion,
                                                    prefijo=prefijo)[0]

    def obtener_puertos(self, string):
        '''
        Parsea y devuelve los puertos que contenga el string pasado por 
        parametro.
        '''
        p = re.compile(REGEX_PUERTO, flags=re.M | re.I)
        for m in p.finditer(string):
            numero = m.groupdict().get('numero')
            protocolo = m.groupdict().get('protocolo') or ''
            protocolo = self.obtener_numero(protocolo)
            yield models.Puerto.objects.get_or_create(numero=numero,
                                                      protocolo=protocolo)[0]

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
