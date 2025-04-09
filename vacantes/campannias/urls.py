from django.urls import path
from campannias import views
from . import views

app_name = 'campannias'

urlpatterns = [
    path('', views.index, name='index'),
    path('google-auth/', views.google_auth_start, name='google_auth_start'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('refrescar-token/', views.refrescar_token),
    path('listar-clientes-ads/', views.listar_clientes_ads),
    path("listar-campanas/", views.listar_campanas_google),
    path('crear-google/', views.crear_campana_google, name='crear_google'),

]