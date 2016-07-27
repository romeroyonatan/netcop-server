from django.test import TestCase

from . import forms, models


class TestCreate(TestCase):

    def setUp(self):
        '''
        Inicializa datos.
        '''
        self.data = {
            'nombre': 'foo',
            'descripcion': 'bar',
            'activa': True,
        }

    def test_parse_subnet(self):
        '''
        Prueba parsear la lista de subredes ingresadas al crear o actualizar
        una clase de tráfico.
        '''
        # preparo parametros
        self.data["subredes_outside"] = """
            191.50.15.0/24
            5.5.0.1
            0.0.0.0/0
            255.255.255.255
        """
        self.data["subredes_inside"] = """
            192.168.1.1
            192.168.2.0/24
            10.200.0.0/16
            10.0.0.0/8
        """
        # creo formulario
        form = forms.ClaseForm(self.data)
        obj = form.save()
        # verifico que todo este bien
        assert form.is_valid()
        self.assertEqual(obj.redes.count(), 8)
        assert (obj.redes.filter(cidr__direccion='192.168.1.1',
                                 cidr__prefijo=32,
                                 grupo=models.INSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='192.168.2.0',
                                 cidr__prefijo=24,
                                 grupo=models.INSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='10.200.0.0',
                                 cidr__prefijo=16,
                                 grupo=models.INSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='10.0.0.0',
                                 cidr__prefijo=8,
                                 grupo=models.INSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='191.50.15.0',
                                 cidr__prefijo=24,
                                 grupo=models.OUTSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='5.5.0.1',
                                 cidr__prefijo=32,
                                 grupo=models.OUTSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='0.0.0.0',
                                 cidr__prefijo=0,
                                 grupo=models.OUTSIDE)
                         .exists())
        assert (obj.redes.filter(cidr__direccion='255.255.255.255',
                                 cidr__prefijo=32,
                                 grupo=models.OUTSIDE)
                         .exists())

    def test_parse_ports(self):
        '''
        Prueba parsear la lista de puertso pasadas al crear o actualizar una
        clase de tráfico.
        '''
        # preparo parametros
        self.data["puertos_outside"] = """
            80/tcp
            443/tcp
            22
            21/udp
        """
        self.data["puertos_inside"] = """
            1025/udp
            65535/UDP
            1
            22
        """
        # creo formulario
        form = forms.ClaseForm(self.data)
        obj = form.save()
        # verifico que todo este bien
        assert form.is_valid()
        self.assertEqual(obj.puertos.count(), 8)
        assert (obj.puertos.filter(puerto__numero=80,
                                   puerto__protocolo=6,
                                   grupo=models.OUTSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=443,
                                   puerto__protocolo=6,
                                   grupo=models.OUTSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=22,
                                   puerto__protocolo=0,
                                   grupo=models.OUTSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=21,
                                   puerto__protocolo=17,
                                   grupo=models.OUTSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=1025,
                                   puerto__protocolo=17,
                                   grupo=models.INSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=65535,
                                   puerto__protocolo=17,
                                   grupo=models.INSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=1,
                                   puerto__protocolo=0,
                                   grupo=models.INSIDE)
                           .exists())
        assert (obj.puertos.filter(puerto__numero=22,
                                   puerto__protocolo=0,
                                   grupo=models.INSIDE)
                           .exists())

    def test_load_subnet(self):
        '''
        Prueba la carga de subredes al actualizar una clase de trafico.
        '''
        # preparo datos
        clase = models.ClaseTrafico.objects.create(
            id=606060,
            nombre='foo',
            descripcion='bar',
        )
        redes_outside = [
            models.CIDR.objects.create(direccion='0.0.0.0', prefijo=0),
            models.CIDR.objects.create(direccion='1.0.0.0', prefijo=1),
            models.CIDR.objects.create(direccion='3.3.3.3', prefijo=32),
        ]
        redes_inside = [
            models.CIDR.objects.create(direccion='10.0.0.0', prefijo=8),
            models.CIDR.objects.create(direccion='172.16.0.0', prefijo=12),
            models.CIDR.objects.create(direccion='192.168.0.0', prefijo=16),
        ]

        for item in redes_outside:
            clase.redes.create(cidr=item, grupo=models.OUTSIDE)

        for item in redes_inside:
            clase.redes.create(cidr=item, grupo=models.INSIDE)
        
        # creo formulario
        form = forms.ClaseForm(instance=clase)
        # verifico que todo este bien
        assert "0.0.0.0/0" in form.initial["subredes_outside"]
        assert "1.0.0.0/1" in form.initial["subredes_outside"]
        assert "3.3.3.3/32" in form.initial["subredes_outside"]
        assert "10.0.0.0/8" in form.initial["subredes_inside"]
        assert "172.16.0.0/12" in form.initial["subredes_inside"]
        assert "192.168.0.0/16" in form.initial["subredes_inside"]

    def test_load_ports(self):
        '''
        Prueba la carga de puertos al actualizar una clase de trafico.
        '''
        # preparo datos
        clase = models.ClaseTrafico.objects.create(
            id=606060,
            nombre='foo',
            descripcion='bar',
        )
        puertos_outside = [
            models.Puerto.objects.create(numero=80, protocolo=6),
            models.Puerto.objects.create(numero=53, protocolo=17),
            models.Puerto.objects.create(numero=22, protocolo=0),
        ]
        puertos_inside = [
            models.Puerto.objects.create(numero=443, protocolo=6),
            models.Puerto.objects.create(numero=137, protocolo=17),
            models.Puerto.objects.create(numero=21, protocolo=0),
        ]

        for item in puertos_outside:
            clase.puertos.create(puerto=item, grupo=models.OUTSIDE)

        for item in puertos_inside:
            clase.puertos.create(puerto=item, grupo=models.INSIDE)
        
        # creo formulario
        form = forms.ClaseForm(instance=clase)
        # verifico que todo este bien
        assert "80/tcp" in form.initial["puertos_outside"]
        assert "53/udp" in form.initial["puertos_outside"]
        assert "22" in form.initial["puertos_outside"]
        assert "443/tcp" in form.initial["puertos_inside"]
        assert "137/udp" in form.initial["puertos_inside"]
        assert "21" in form.initial["puertos_inside"]
        
    def test_validate_subnet(self):
        '''
        Prueba la validacion de subredes en el formulario de clases.
        '''
        pass

    def test_validate_ports(self):
        '''
        Prueba la validacion de puertos en el formulario de clases.
        '''
        pass

    def test_list(self):
        '''
        Prueba obtener la lista de clases de trafico instaladas.
        '''
        pass

    def test_json(self):
        '''
        Prueba obtener la lista de clases de trafico instaladas en formato JSON
        '''
        pass

    def test_version(self):
        '''
        Prueba obtener el numero de version de las clases instaladas.
        '''
        pass
