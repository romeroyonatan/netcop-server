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
        pass

    def test_load_ports(self):
        '''
        Prueba la carga de puertos al actualizar una clase de trafico.
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
