from django.urls import path
from . import views

app_name = 'vacantes'

urlpatterns = [
    path('crear/', views.crear_vacante, name='crear_vacante'),
    path('', views.listar_vacantes, name='listar_vacantes'),
    path('eliminar/<int:vacante_id>/', views.eliminar_vacante, name='eliminar_vacante'),
    path('gestion/', views.gestion_vacantes, name='gestion_vacantes'),
    path('editar/<int:vacante_id>/', views.editar_vacante, name='editar_vacante'),
]