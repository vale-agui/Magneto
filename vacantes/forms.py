from django import forms
from .models import Vacante

class VacanteForm(forms.ModelForm):
    class Meta:
        model = Vacante
        fields = ['nombre', 'edad', 'genero', 'especialidad']
