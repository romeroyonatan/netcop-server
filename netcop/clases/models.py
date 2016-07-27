from django.db import models

INSIDE = 'i'
OUTSIDE = 'o'

grupo_choices = (
    (INSIDE, "En la red local"),
    (OUTSIDE, "En Internet"),
)

class ClaseTrafico(models.Model):
    nombre = models.CharField(max_length=32, null=False)
    descripcion = models.CharField(max_length=160, null=False, default="")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class CIDR(models.Model):
    direccion = models.GenericIPAddressField(protocol='IPv4')
    prefijo = models.PositiveSmallIntegerField(default=32)

    def __str__(self):
        return "%s/%d" % (self.direccion, self.prefijo)


class Puerto(models.Model):
    numero = models.PositiveIntegerField()
    protocolo = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        protocolo = ''
        if self.protocolo == 6:
            protocolo = '/tcp'
        elif self.protocolo == 17:
            protocolo = '/udp'
        return "%d%s" % (self.numero, protocolo)


class ClaseCIDR(models.Model):
    clase = models.ForeignKey(ClaseTrafico, related_name="redes")
    cidr = models.ForeignKey(CIDR, related_name="clases")
    grupo = models.CharField(max_length=1, choices=grupo_choices)


class ClasePuerto(models.Model):
    choices = (
        (INSIDE, "En la red local"),
        (OUTSIDE, "En Internet"),
    )
    clase = models.ForeignKey(ClaseTrafico, related_name="puertos")
    puerto = models.ForeignKey(Puerto, related_name="clases")
    grupo = models.CharField(max_length=1, choices=grupo_choices)
