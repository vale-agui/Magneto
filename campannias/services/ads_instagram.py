# services/ads_instagram.py

from django.http import JsonResponse
from datetime import datetime, timedelta
import random
from ..models import CampanaInstagram

# Configuración de credenciales simuladas según Instagram Graph API
MOCK_CREDENTIALS = {
    "access_token": "mock_instagram_access_token",
    "app_id": "mock_instagram_app_id",
    "app_secret": "mock_instagram_app_secret",
    "instagram_account_id": "17895695666004550",
    "business_id": "123456789",
    "token_expiry": (datetime.now() + timedelta(hours=1)).isoformat(),
    "token_type": "Bearer",
    "graph_version": "v18.0"
}

# Cuentas simuladas según estructura de Instagram Business
MOCK_ACCOUNTS = [
    {
        "id": "17895695666004550",
        "name": "Cuenta Instagram 1",
        "username": "cuenta_instagram_1",
        "profile_picture_url": "https://example.com/profile1.jpg",
        "account_type": "BUSINESS",
        "business_id": "123456789",
        "business_name": "Negocio 1",
        "followers_count": 1000,
        "media_count": 50,
        "currency": "MXN",
        "timezone": "America/Mexico_City",
        "permissions": ["MANAGE", "ADVERTISE"],
        "capabilities": ["MANAGE_ADS", "MANAGE_CAMPAIGNS"]
    },
    {
        "id": "17895695666004551",
        "name": "Cuenta Instagram 2",
        "username": "cuenta_instagram_2",
        "profile_picture_url": "https://example.com/profile2.jpg",
        "account_type": "BUSINESS",
        "business_id": "987654321",
        "business_name": "Negocio 2",
        "followers_count": 2000,
        "media_count": 100,
        "currency": "MXN",
        "timezone": "America/Mexico_City",
        "permissions": ["MANAGE", "ADVERTISE"],
        "capabilities": ["MANAGE_ADS", "MANAGE_CAMPAIGNS"]
    }
]

def guardar_campana_instagram(request, datos):
    """Guarda una campaña de Instagram en la base de datos."""
    campana = CampanaInstagram(
        image_url=datos.get('image_url'),
        caption=datos.get('caption', ''),
        access_token=datos.get('access_token'),
        nombre=datos.get('nombre'),
        presupuesto=datos.get('presupuesto'),
        fecha_inicio=datos.get('fecha_inicio'),
        fecha_fin=datos.get('fecha_fin'),
        objetivo=datos.get('objetivo'),
        tipo_contenido=datos.get('tipo_contenido'),
        formato_anuncio=datos.get('formato_anuncio'),
        ubicacion_anuncio=datos.get('ubicacion_anuncio'),
        edad_min=datos.get('edad_min'),
        edad_max=datos.get('edad_max'),
        genero=datos.get('genero'),
        ubicacion=datos.get('ubicacion'),
        intereses=datos.get('intereses'),
        hashtags=datos.get('hashtags', ''),
        url_redireccion=datos.get('url_redireccion'),
        usuario=request.user
    )
    campana.save()
    return campana

# def validar_requisitos_instagram(datos):
#     return {'valido': True, 'datos_validados': datos}

def listar_campanas_instagram(request):
    """
    Lista las campañas de Instagram Ads desde la base de datos.
    """
    try:
        campanias = CampanaInstagram.objects.filter(usuario=request.user).order_by('-fecha_creacion')
        resultados = []
        
        for campania in campanias:
            resultados.append({
                "id": campania.id,
                "nombre": campania.nombre,
                "estado": campania.estado,
                "objetivo": campania.objetivo,
                "presupuesto": campania.presupuesto,
                "fecha_inicio": campania.fecha_inicio,
                "fecha_fin": campania.fecha_fin,
                "audiencia": campania.audiencia,
                "ubicaciones": campania.ubicaciones,
                "intereses": campania.intereses
            })
        
        return resultados
    except Exception as e:
        return {"error": str(e)}
