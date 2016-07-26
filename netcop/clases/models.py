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


class CIDR(models.Model):
    direccion = models.GenericIPAddressField(protocol='IPv4')
    prefijo = models.PositiveSmallIntegerField(default=32)


class Puerto(models.Model):
    numero = models.PositiveIntegerField()
    protocolo = models.PositiveSmallIntegerField(default=0)


class ClaseCIDR(models.Model):
    clase = models.ForeignKey(ClaseTrafico)
    cidr = models.ForeignKey(CIDR)
    grupo = models.CharField(max_length=1, choices=grupo_choices)


class ClasePuerto(models.Model):
    choices = (
        (INSIDE, "En la red local"),
        (OUTSIDE, "En Internet"),
    )
    clase = models.ForeignKey(ClaseTrafico)
    puerto = models.ForeignKey(Puerto)
    grupo = models.CharField(max_length=1, choices=grupo_choices)
