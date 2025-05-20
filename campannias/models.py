from django.db import models
from django.contrib.auth.models import User

class CampaniaBase(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada')
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CampaniaFacebook(CampaniaBase):
    # Campos específicos de Facebook
    tipo_anuncio = models.CharField(max_length=50, choices=[
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('carousel', 'Carousel'),
        ('coleccion', 'Colección')
    ])
    formato_anuncio = models.CharField(max_length=50)
    ubicacion_anuncio = models.CharField(max_length=50)
    segmentacion_edad_min = models.IntegerField()
    segmentacion_edad_max = models.IntegerField()
    segmentacion_genero = models.CharField(max_length=20)
    segmentacion_ubicacion = models.CharField(max_length=200)
    segmentacion_intereses = models.TextField()
    idioma = models.CharField(max_length=50)
    dispositivo = models.CharField(max_length=50)
    comportamiento = models.TextField()

    def __str__(self):
        return f"Facebook - {self.nombre}"

class CampaniaInstagram(CampaniaBase):
    # Campos específicos de Instagram
    tipo_contenido = models.CharField(max_length=50, choices=[
        ('historia', 'Historia'),
        ('post', 'Post'),
        ('reels', 'Reels'),
        ('carousel', 'Carousel')
    ])
    formato_anuncio = models.CharField(max_length=50)
    ubicacion_anuncio = models.CharField(max_length=50)
    segmentacion_edad_min = models.IntegerField()
    segmentacion_edad_max = models.IntegerField()
    segmentacion_genero = models.CharField(max_length=20)
    segmentacion_ubicacion = models.CharField(max_length=200)
    segmentacion_intereses = models.TextField()
    hashtags = models.TextField()
    estilo_visual = models.CharField(max_length=50)
    tono_mensaje = models.CharField(max_length=50)

    def __str__(self):
        return f"Instagram - {self.nombre}"

class CampaniaGoogle(CampaniaBase):
    # Campos específicos de Google Ads
    tipo_campana = models.CharField(max_length=50, choices=[
        ('busqueda', 'Búsqueda'),
        ('display', 'Display'),
        ('video', 'Video'),
        ('shopping', 'Shopping')
    ])
    red_anuncios = models.CharField(max_length=50)
    segmentacion_edad_min = models.IntegerField()
    segmentacion_edad_max = models.IntegerField()
    segmentacion_genero = models.CharField(max_length=20)
    segmentacion_ubicacion = models.CharField(max_length=200)
    segmentacion_intereses = models.TextField()
    palabras_clave = models.TextField()
    presupuesto_diario = models.DecimalField(max_digits=10, decimal_places=2)
    puja_maxima = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Google - {self.nombre}"

class ResultadoCampania(models.Model):
    campania_facebook = models.ForeignKey(CampaniaFacebook, on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_facebook')
    campania_instagram = models.ForeignKey(CampaniaInstagram, on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_instagram')
    campania_google = models.ForeignKey(CampaniaGoogle, on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_google')
    fecha = models.DateField()
    impresiones = models.IntegerField(default=0)
    clics = models.IntegerField(default=0)
    conversiones = models.IntegerField(default=0)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        campania = self.campania_facebook or self.campania_instagram or self.campania_google
        return f"Resultados de {campania} - {self.fecha}"