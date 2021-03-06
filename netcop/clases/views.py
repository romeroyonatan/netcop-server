import os
import re
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.http import JsonResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import models, forms


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(*args, **kwargs)
        return login_required(view)


class ClaseList(generic.ListView):
    model = models.ClaseTrafico
    ordering = ('-activa', 'id')

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        q = self.request.GET.get('q')
        if q:
            filters = (Q(nombre__icontains=q) |
                       Q(descripcion__icontains=q) |
                       Q(redes__cidr__direccion__contains=q))
            if re.match("^\d+$", q):
                filters |= Q(puertos__puerto__numero=q)
                filters |= Q(pk=q)
            qs = qs.filter(filters).distinct()
        return qs


class ClaseCreate(LoginRequiredMixin, generic.CreateView):
    model = models.ClaseTrafico
    success_url = reverse_lazy('index')
    form_class = forms.ClaseForm


class ClaseUpdate(LoginRequiredMixin, generic.UpdateView):
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
