from django.urls import path
from . import views
from .views import actualizar_tokens_view
from .services.gestion_campannias import seleccionar_redes
from .services.gestion_campannias import crear_campania_dinamica
from . import views

app_name = 'campannias'

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    
    # Vistas de creación de campañas
    path('crear/google/', views.crear_google_view, name='crear_google_view'),
    path('crear/facebook/', views.crear_facebook_view, name='crear_facebook_view'),
    path('crear/instagram/', views.crear_instagram_view, name='crear_instagram_view'),
    
    # Endpoints de autenticación
  
    
    # Endpoints de listados y métricas
    path('api/listar/google/campanas/', views.listar_campanas_google_view, name='listar_campanas_google'),
    path('api/listar/google/clientes/', views.listar_clientes_ads_view, name='listar_clientes_ads'),
    path('api/listar/facebook/cuentas/', views.listar_cuentas_facebook, name='listar_cuentas_facebook'),
    path('listar/', views.listar_campanias, name='listar_campanias'),
    path('seleccionar-redes/', seleccionar_redes, name='seleccionar_redes'),
    path('crear-campania-dinamica/', crear_campania_dinamica, name='crear_campania_dinamica'),

    
    # Nuevas URLs para gestión de campañas
    path('total-gastado/', views.total_gastado, name='total_gastado'),
    path('costo-por-campania/', views.costo_por_campania, name='costo_por_campania'),
    path('reutilizar-campanias/', views.reutilizar_campanias, name='reutilizar_campanias'),
    path('actualizar-tokens/', actualizar_tokens_view, name='actualizar_tokens'),
    path('detener-campania/<int:pk>/<str:tipo>/', views.detener_campania, name='detener_campania'),
]
