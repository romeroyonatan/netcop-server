from django import forms

from . import models

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

    def save(self, *args, **kwargs):
        clase = super().save(*args, **kwargs)
        self.actualizar_colecciones(clase, self.cleaned_data)
        return clase

    def actualizar_colecciones(self, clase, nueva):
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
        for lista, grupo in redes:
            for item in nueva.get(lista, "").split("\n"):
                if item:
                    (direccion, prefijo) = item.split('/')
                    # TODO validar
                    cidr = models.CIDR.objects.get_or_create(
                        direccion=direccion,
                        prefijo=prefijo
                    )[0]
                    models.ClaseCIDR.objects.create(clase=clase,
                                                    cidr=cidr,
                                                    grupo=grupo)

        for lista, grupo in puertos:
            for item in nueva.get(lista, "").split("\n"):
                if item:
                    (numero, proto) = item.split('/')
                    # TODO validar
                    protocolo = self.protocolo(proto)
                    puerto = models.Puerto.objects.get_or_create(
                        numero=numero,
                        protocolo=protocolo
                    )[0]
                    models.ClasePuerto.objects.create(clase=clase,
                                                      puerto=puerto,
                                                      grupo=grupo)

    def protocolo(self, string):
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
