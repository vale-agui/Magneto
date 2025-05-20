from django import forms
from .models import CampaniaFacebook, CampaniaInstagram, CampaniaGoogle

class CampaniaFacebookForm(forms.ModelForm):
    class Meta:
        model = CampaniaFacebook
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

class CampaniaInstagramForm(forms.ModelForm):
    class Meta:
        model = CampaniaInstagram
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

class CampaniaGoogleForm(forms.ModelForm):
    class Meta:
        model = CampaniaGoogle
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

# Aquí puedes definir los formularios ModelForm para cada modelo si los necesitas
# Por ejemplo:
# class CampaniaFacebookForm(forms.ModelForm):
#     class Meta:
#         model = CampaniaFacebook
#         fields = '__all__'
