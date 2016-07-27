import os
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.http import JsonResponse, Http404
from django.conf import settings

from . import models, forms


class ClaseList(generic.ListView):
    model = models.ClaseTrafico
    ordering = ('-activa', 'id')

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__contains=q)
        return qs


class ClaseCreate(generic.CreateView):
    model = models.ClaseTrafico
    success_url = reverse_lazy('index')
    form_class = forms.ClaseForm


class ClaseUpdate(generic.UpdateView):
    model = models.ClaseTrafico
    form_class = forms.ClaseForm
    success_url = reverse_lazy('index')


class ClaseJson(generic.View):
    '''
    Devuelve las clases en formato json.
    '''

    def get(self, *args, **kwargs):
        return JsonResponse({'clases': self.obtener_clases()})

    def obtener_clases(self):
        lista = list()
        for clase in models.ClaseTrafico.objects.all().order_by('id'):
            r = dict()
            r['id'] = clase.id
            r['nombre'] = clase.nombre
            r['descripcion'] = clase.descripcion
            r['activa'] = clase.activa
            r['subredes_outside'] = [
                str(item) for item in clase.redes.filter(grupo=models.OUTSIDE)
            ]
            r['subredes_inside'] = [
                str(item) for item in clase.redes.filter(grupo=models.INSIDE)
            ]
            r['puertos_outside'] = [
                str(item) for item in clase.puertos.filter(
                    grupo=models.OUTSIDE)
            ]
            r['puertos_inside'] = [
                str(item) for item in clase.puertos.filter(grupo=models.INSIDE)
            ]
            lista.append(r)
        return lista


class VersionView(ClaseJson):
    '''
    Devuelve numero de version de la base de datos de firmas.

    Lo obtiene haciendo una suma SHA256 del json de las clases.
    '''
    def get(self, *args, **kwargs):
        path = os.path.join(settings.MEDIA_ROOT, 'version')
        with open(path, 'r') as f:
            version = f.read()
        if not version:
            raise Http404()
        return JsonResponse({"version": str(version)})
