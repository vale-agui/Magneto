from django.urls import path
from . import views

app_name = 'campannias'

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    
    # Vistas de creación de campañas
    path('crear/google/', views.crear_google_view, name='crear_google_view'),
    path('crear/facebook/', views.crear_facebook_view, name='crear_facebook_view'),
    path('crear/instagram/', views.crear_instagram_view, name='crear_instagram_view'),
    
    # Endpoints para procesar campañas
    path('api/crear/google/', views.crear_campana_google, name='crear_campana_google'),
    path('api/crear/facebook/', views.crear_campana_facebook, name='crear_campana_facebook'),
    path('api/crear/instagram/', views.crear_campana_instagram, name='crear_campana_instagram'),
    
    # Endpoints de autenticación
    path('auth/google/start/', views.google_auth_start, name='google_auth_start'),
    path('auth/google/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('auth/facebook/start/', views.facebook_auth_start, name='facebook_auth_start'),
    path('auth/facebook/callback/', views.facebook_auth_callback, name='facebook_auth_callback'),
    
    # Endpoints de listados y métricas
    path('api/listar/google/campanas/', views.listar_campanas_google_view, name='listar_campanas_google'),
    path('api/listar/google/clientes/', views.listar_clientes_ads_view, name='listar_clientes_ads'),
    path('api/listar/facebook/cuentas/', views.listar_cuentas_facebook, name='listar_cuentas_facebook'),
    path('api/preview/<int:pk>/', views.preview_anuncio, name='preview_anuncio'),
    path('api/metricas/<int:pk>/', views.obtener_metricas, name='obtener_metricas'),
    path('listar/', views.listar_campanias, name='listar_campanias'),
    path('seleccionar-redes/', views.seleccionar_redes, name='seleccionar_redes'),
    path('crear-campania-dinamica/', views.crear_campania_dinamica, name='crear_campania_dinamica'),
    
    # Nuevas URLs para gestión de campañas
    path('total-gastado/', views.total_gastado, name='total_gastado'),
    path('costo-por-campania/', views.costo_por_campania, name='costo_por_campania'),
    path('reutilizar-campanias/', views.reutilizar_campanias, name='reutilizar_campanias'),
]
