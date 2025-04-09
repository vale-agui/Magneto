from django.urls import path
from campannias import views
from . import views

app_name = 'campannias'

urlpatterns = [
    path('', views.index, name='index'),

    #google
    path('google-auth/', views.google_auth_start, name='google_auth_start'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('refrescar-token/', views.refrescar_token),
    path('listar-clientes-ads/', views.listar_clientes_ads),
    path("listar-campanas/", views.listar_campanas_google),
    path('crear-google/', views.crear_campana_google, name='crear_google'),

    # Facebook
    path('crear-facebook/', views.crear_campana_facebook, name='crear_facebook'),
    path('crear-campana-facebook/', views.crear_campana_facebook, name='crear_campana_facebook'),
    path('facebook-auth/', views.facebook_auth_start, name='facebook_auth_start'),  # ✅ ESTA ES LA QUE TE FALTA
    path('facebook-callback/', views.facebook_callback, name='facebook_callback'),
    path('listar-cuentas-facebook/', views.listar_cuentas_facebook, name='listar_cuentas_facebook'),
]