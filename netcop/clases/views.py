from django.core.urlresolvers import reverse_lazy
from django.views import generic

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
