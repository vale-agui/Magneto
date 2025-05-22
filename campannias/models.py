from django.db import models
from django.contrib.auth.models import User
from datetime import time, date

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
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField(default=time(0, 0))
    fecha_fin = models.DateField()
    hora_fin = models.TimeField(default=time(23, 59))

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
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField(default=time(0, 0))
    fecha_fin = models.DateField()
    hora_fin = models.TimeField(default=time(23, 59))

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
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField(default=time(0, 0))
    fecha_fin = models.DateField()
    hora_fin = models.TimeField(default=time(23, 59))

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

class CampanaFacebook(models.Model):
    ESTADOS = [
        ('ACTIVE', 'Activa'),
        ('PAUSED', 'Pausada'),
    ]
    
    TIPOS_PRESUPUESTO = [
        ('daily_budget', 'Presupuesto Diario'),
        ('lifetime_budget', 'Presupuesto Total'),
    ]
    
    EVENTOS_COBRO = [
        ('IMPRESSIONS', 'Impresiones'),
        ('CLICKS', 'Clics'),
        ('LINK_CLICKS', 'Clics en Enlaces'),
        ('VIDEO_VIEWS', 'Vistas de Video'),
    ]
    
    OBJETIVOS = [
        ('LINK_CLICKS', 'Clics en Enlaces'),
        ('REACH', 'Alcance'),
        ('IMPRESSIONS', 'Impresiones'),
        ('VIDEO_VIEWS', 'Vistas de Video'),
        ('POST_ENGAGEMENT', 'Interacción con Publicaciones'),
    ]
    
    GENEROS = [
        ('ALL', 'Todos'),
        ('MALE', 'Masculino'),
        ('FEMALE', 'Femenino'),
    ]

    # Campos básicos
    nombre = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255)
    
    # Configuración de presupuesto
    tipo_presupuesto = models.CharField(max_length=20, choices=TIPOS_PRESUPUESTO)
    monto_presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    evento_cobro = models.CharField(max_length=20, choices=EVENTOS_COBRO)
    objetivo_optimizacion = models.CharField(max_length=20, choices=OBJETIVOS)
    
    # Segmentación
    edad_min = models.IntegerField()
    edad_max = models.IntegerField()
    genero = models.CharField(max_length=10, choices=GENEROS)
    ubicaciones = models.TextField()  # Almacenará ubicaciones separadas por comas
    intereses = models.TextField(blank=True)  # Almacenará intereses separados por comas
    
    # Estado
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PAUSED')
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(default=date.today)
    hora_inicio = models.TimeField(default=time(0, 0))
    fecha_fin = models.DateField(default=date.today)
    hora_fin = models.TimeField(default=time(23, 59))
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Campaña Facebook"
        verbose_name_plural = "Campañas Facebook"
        ordering = ['-fecha_creacion']

class CampanaGoogle(models.Model):
    ESTADOS = [
        ('ACTIVE', 'Activa'),
        ('PAUSED', 'Pausada'),
    ]
    
    TIPOS_CAMPANA = [
        ('SEARCH', 'Búsqueda'),
        ('DISPLAY', 'Display'),
        ('VIDEO', 'Video'),
        ('SHOPPING', 'Shopping'),
    ]
    
    # Campos de autenticación y configuración
    customer_id = models.CharField(max_length=255, help_text="ID de cliente de Google Ads")
    developer_token = models.CharField(max_length=255, help_text="Developer Token de Google Ads")
    refresh_token = models.CharField(max_length=255, help_text="Refresh Token de OAuth 2.0")
    access_token = models.CharField(max_length=255, help_text="Access Token de OAuth 2.0")
    mcc_account = models.BooleanField(default=False, help_text="Indica si es una cuenta MCC")
    
    # Campos básicos de la campaña
    nombre = models.CharField(max_length=255)
    tipo_campana = models.CharField(max_length=20, choices=TIPOS_CAMPANA)
    presupuesto_diario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField(default=date.today)
    hora_inicio = models.TimeField(default=time(0, 0))
    fecha_fin = models.DateField(default=date.today)
    hora_fin = models.TimeField(default=time(23, 59))
    
    # Configuración de segmentación
    palabras_clave = models.TextField(help_text="Palabras clave separadas por comas")
    ubicaciones = models.TextField(help_text="Ubicaciones objetivo separadas por comas")
    idiomas = models.TextField(help_text="Idiomas objetivo separados por comas")
    
    # Configuración de pujas
    puja_maxima = models.DecimalField(max_digits=10, decimal_places=2)
    estrategia_puja = models.CharField(max_length=50, choices=[
        ('MANUAL_CPC', 'CPC Manual'),
        ('MAXIMIZE_CONVERSIONS', 'Maximizar Conversiones'),
        ('TARGET_CPA', 'CPA Objetivo'),
        ('TARGET_ROAS', 'ROAS Objetivo'),
    ])
    
    # Estado y metadatos
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PAUSED')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Campaña Google"
        verbose_name_plural = "Campañas Google"
        ordering = ['-fecha_creacion']