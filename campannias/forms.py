from django import forms
from .models import CampanaFacebook, CampaniaInstagram, CampanaGoogle

class CampaniaFacebookForm(forms.ModelForm):
    class Meta:
        model = CampanaFacebook
        fields = ['nombre', 'campaign_id', 'tipo_presupuesto', 'monto_presupuesto', 
                 'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin',
                 'evento_cobro', 'objetivo_optimizacion', 'edad_min',
                 'edad_max', 'genero', 'ubicaciones', 'intereses', 'estado']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'intereses': forms.Textarea(attrs={'rows': 3}),
            'ubicaciones': forms.Textarea(attrs={'rows': 3}),
        }

class CampaniaInstagramForm(forms.ModelForm):
    class Meta:
        model = CampaniaInstagram
        fields = ['nombre', 'tipo_contenido', 'formato_anuncio', 'ubicacion_anuncio',
                 'segmentacion_edad_min', 'segmentacion_edad_max', 'segmentacion_genero',
                 'segmentacion_ubicacion', 'segmentacion_intereses', 'hashtags',
                 'estilo_visual', 'tono_mensaje', 'fecha_inicio', 'hora_inicio',
                 'fecha_fin', 'hora_fin', 'presupuesto', 'estado']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'segmentacion_intereses': forms.Textarea(attrs={'rows': 3}),
            'segmentacion_ubicacion': forms.Textarea(attrs={'rows': 3}),
            'hashtags': forms.Textarea(attrs={'rows': 3}),
        }

class CampaniaGoogleForm(forms.ModelForm):
    class Meta:
        model = CampanaGoogle
        fields = ['nombre', 'customer_id', 'developer_token', 'tipo_campana',
                 'presupuesto_diario', 'fecha_inicio', 'hora_inicio', 'fecha_fin',
                 'hora_fin', 'palabras_clave', 'ubicaciones', 'idiomas',
                 'puja_maxima', 'estrategia_puja', 'estado']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'palabras_clave': forms.Textarea(attrs={'rows': 3}),
            'ubicaciones': forms.Textarea(attrs={'rows': 3}),
            'idiomas': forms.Textarea(attrs={'rows': 3}),
        }

# Aquí puedes definir los formularios ModelForm para cada modelo si los necesitas
# Por ejemplo:
# class CampaniaFacebookForm(forms.ModelForm):
#     class Meta:
#         model = CampaniaFacebook
#         fields = '__all__'
