from django.core.urlresolvers import reverse_lazy
from django.views import generic

from . import models


class ClaseList(generic.ListView):
    model = models.ClaseTrafico
    ordering = ('-activa', 'nombre')

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__contains=q)
        return qs


class ClaseCreate(generic.CreateView):
    model = models.ClaseTrafico
    fields = '__all__'
    success_url = reverse_lazy('index')


class ClaseUpdate(generic.UpdateView):
    model = models.ClaseTrafico
    fields = '__all__'
    success_url = reverse_lazy('index')
