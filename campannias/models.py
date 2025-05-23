from django.db import models
from django.contrib.auth.models import User
from datetime import time, date

class CampaniaBase(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
        ('FINALIZADA', 'Finalizada'),
    ]
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def detener(self):
        if self.estado == 'ACTIVA':
            self.estado = 'PAUSADA'
            self.save()
            return True
        return False

    class Meta:
        abstract = True

class CampanaFacebook(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
    ]
    
    TIPOS_PRESUPUESTO = [
        ('PRESUPUESTO_DIARIO', 'Presupuesto Diario'),
        ('PRESUPUESTO_TOTAL', 'Presupuesto Total'),
    ]
    
    EVENTOS_COBRO = [
        ('IMPRESIONES', 'Impresiones'),
        ('CLICS', 'Clics'),
        ('CLICS_EN_ENLACES', 'Clics en Enlaces'),
        ('VISTAS_DE_VIDEO', 'Vistas de Video'),
    ]
    
    OBJETIVOS = [
        ('CLICS_EN_ENLACES', 'Clics en Enlaces'),
        ('ALCANCE', 'Alcance'),
        ('IMPRESIONES', 'Impresiones'),
        ('VISTAS_DE_VIDEO', 'Vistas de Video'),
        ('INTERACCION_CON_PUBLICACIONES', 'Interacción con Publicaciones'),
    ]
    
    GENEROS = [
        ('TODOS', 'Todos'),
        ('MASCULINO', 'Masculino'),
        ('FEMENINO', 'Femenino'),
    ]

    # Campos básicos
    nombre = models.CharField(max_length=255, null=True)
    campaign_id = models.CharField(max_length=255, null=True)
    
    # Configuración de presupuesto
    tipo_presupuesto = models.CharField(max_length=20, choices=TIPOS_PRESUPUESTO, null=True)
    monto_presupuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    evento_cobro = models.CharField(max_length=20, choices=EVENTOS_COBRO, null=True)
    objetivos = models.CharField(max_length=50, choices=OBJETIVOS, null=True)
    
    # Segmentación
    edad_min = models.IntegerField(null=True)
    edad_max = models.IntegerField(null=True)
    genero = models.CharField(max_length=10, choices=GENEROS, null=True)
    ubicaciones = models.TextField(null=True)
    intereses = models.TextField(blank=True, null=True)
    
    # Estado
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PAUSED', null=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(default=date.today, null=True)
    fecha_fin = models.DateField(default=date.today, null=True)
    
    url_redireccion = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Campaña Facebook"
        verbose_name_plural = "Campañas Facebook"
        ordering = ['-fecha_creacion']

class CampanaInstagram(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
        ('FINALIZADA', 'Finalizada'),
    ]
    
    # Contenido de Instagram
    image_url = models.URLField(null=True)
    caption = models.TextField(blank=True, null=True)
    access_token = models.CharField(max_length=255, null=True)

    # Configuración de campaña
    nombre = models.CharField(max_length=255, null=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA')

    # Configuración de anuncio
    objetivo = models.CharField(max_length=100, null=True)
    tipo_contenido = models.CharField(max_length=50, choices=[
        ('historia', 'Historia'),
        ('post', 'Post'),
        ('reels', 'Reels'),
        ('carousel', 'Carousel')
    ], null=True)
    formato_anuncio = models.CharField(max_length=50, null=True)
    ubicacion_anuncio = models.CharField(max_length=50, null=True)

    # Segmentación
    edad_min = models.IntegerField(null=True)
    edad_max = models.IntegerField(null=True)
    genero = models.CharField(max_length=20, choices=[
        ('todos', 'Todos'),
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino')
    ], null=True)
    ubicacion = models.CharField(max_length=200, null=True)
    intereses = models.TextField(null=True)
    hashtags = models.TextField(blank=True, null=True)

    # Metadatos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    url_redireccion = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Instagram - {self.nombre}"

class ResultadoCampania(models.Model):
    campania_facebook = models.ForeignKey(CampanaFacebook, on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_facebook')
    campania_instagram = models.ForeignKey(CampanaInstagram, on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_instagram')
    campania_google = models.ForeignKey('CampanaGoogle', on_delete=models.CASCADE, null=True, blank=True, related_name='resultados_google')
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

class CampanaGoogle(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
    ]
    # Configuración de campaña
    nombre = models.CharField(max_length=255, null=True)
    tipo_campana = models.CharField(max_length=20, choices=[
        ('SEARCH', 'Búsqueda'),
        ('DISPLAY', 'Display'),
        ('VIDEO', 'Video'),
        ('SHOPPING', 'Shopping'),
    ], null=True)
    presupuesto_diario = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PAUSADA', null=True)

    # Configuración de anuncios
    palabras_clave = models.TextField(help_text="Palabras clave separadas por comas", null=True)
    ubicaciones = models.TextField(help_text="Ubicaciones objetivo separadas por comas", null=True)
    idiomas = models.TextField(help_text="Idiomas objetivo separados por comas", null=True)
    puja_maxima = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    estrategia_puja = models.CharField(max_length=50, choices=[
        ('MANUAL_CPC', 'CPC Manual'),
        ('MAXIMIZE_CONVERSIONS', 'Maximizar Conversiones'),
        ('TARGET_CPA', 'CPA Objetivo'),
        ('TARGET_ROAS', 'ROAS Objetivo'),
    ], null=True)

    # Metadatos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.tipo_campana}"

    class Meta:
        verbose_name = "Campaña Google"
        verbose_name_plural = "Campañas Google"
        ordering = ['-fecha_creacion']