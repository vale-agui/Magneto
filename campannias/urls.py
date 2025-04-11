from django.urls import path
from . import views

app_name = 'campannias'

urlpatterns = [
    path('', views.index, name='index'),
    # Rutas de Google (se mantienen según lo configurado)
    path('google-auth/', views.google_auth_start, name='google_auth_start'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('refrescar-token/', views.refrescar_token),
    path('listar-clientes-ads/', views.listar_clientes_ads_view, name='listar_clientes_ads'),
    path("listar-campanas/", views.listar_campanas_google_view, name='listar_campanas'),
    path('crear-google-form/', views.crear_google_view, name='crear_google_view'),
    path('crear-google/', views.crear_campana_google, name='crear_google'),
    # Rutas de Facebook
    path('crear-facebook-form/', views.crear_facebook_view, name='crear_facebook_view'),
    path('crear-facebook/', views.crear_campana_facebook, name='crear_facebook'),
    path('facebook-auth/', views.facebook_auth_start, name='facebook_auth_start'),
    path('facebook-callback/', views.facebook_callback, name='facebook_callback'),
    path('listar-cuentas-facebook/', views.listar_cuentas_facebook, name='listar_cuentas_facebook'),
    # Rutas de Instagram (si aplica)
    path('crear-instagram-form/', views.crear_instagram_view, name='crear_instagram_view'),
    path('crear-instagram/', views.crear_campana_instagram, name='crear_instagram'),
]
