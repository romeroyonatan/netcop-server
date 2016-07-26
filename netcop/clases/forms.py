from django import forms

from . import models

class ClaseForm(forms.ModelForm):
    '''
    Formulario para agilizar la creación de clases de trafico.
    '''

    class Meta:
        model = models.ClaseTrafico
        fields = '__all__'
