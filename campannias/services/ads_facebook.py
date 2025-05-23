# services/ads_facebook.py

import os
from datetime import datetime, timedelta
import random
import json
from django.http import JsonResponse
from ..models import CampanaFacebook

# Configuración de credenciales simuladas según Facebook Marketing API
MOCK_CREDENTIALS = {
    "access_token": "mock_facebook_access_token",
    "app_id": "mock_facebook_app_id",
    "app_secret": "mock_facebook_app_secret",
    "ad_account_id": "act_123456789",
    "business_id": "123456789",
    "token_expiry": (datetime.now() + timedelta(hours=1)).isoformat(),
    "token_type": "Bearer",
    "graph_version": "v18.0"
}

# Cuentas simuladas según estructura de Facebook Business Manager
MOCK_ACCOUNTS = [
    {
        "id": "act_123456789",
        "name": "Cuenta Facebook 1",
        "account_status": 1,
        "currency": "MXN",
        "timezone": "America/Colombia",
        "business_name": "Negocio 1",
        "business_id": "123456789",
        "permissions": ["MANAGE", "ADVERTISE"],
        "capabilities": ["MANAGE_ADS", "MANAGE_CAMPAIGNS"]
    },
    {
        "id": "act_987654321",
        "name": "Cuenta Facebook 2",
        "account_status": 1,
        "currency": "MXN",
        "timezone": "America/Colombia",
        "business_name": "Negocio 2",
        "business_id": "987654321",
        "permissions": ["MANAGE", "ADVERTISE"],
        "capabilities": ["MANAGE_ADS", "MANAGE_CAMPAIGNS"]
    }
]

def facebook_auth_url():
    """Simula la URL de autenticación de Facebook"""
    return "https://www.facebook.com/v18.0/dialog/oauth?mock=true", None

def facebook_callback_logic(request):
    """Simula el manejo del callback de autenticación de Facebook"""
    return MOCK_CREDENTIALS, None

def listar_cuentas_facebook_service():
    """Simula la obtención de cuentas de Facebook Ads"""
    return MOCK_ACCOUNTS

def listar_campanas_facebook(request):
    """
    Lista las campañas de Facebook Ads desde la base de datos.
    """
    try:
        campanias = CampanaFacebook.objects.filter(usuario=request.user).order_by('-fecha_creacion')
        resultados = []
        
        for campania in campanias:
            resultados.append({
                "id": campania.id,
                "nombre": campania.nombre,
                "estado": campania.estado,
                "presupuesto": campania.monto_presupuesto,
                "fecha_inicio": campania.fecha_inicio,
                "fecha_fin": campania.fecha_fin,
                "objetivo": campania.objetivo_optimizacion,
                "audiencia": {
                    "edad_min": campania.edad_min,
                    "edad_max": campania.edad_max,
                    "genero": campania.genero,
                    "ubicaciones": campania.ubicaciones,
                    "intereses": campania.intereses
                }
            })
        
        return resultados
    except Exception as e:
        return {"error": str(e)}

def guardar_campana_facebook(request, datos):
    campana = CampanaFacebook(
        nombre=datos.get('nombre'),
        campaign_id=datos.get('campaign_id'),
        tipo_presupuesto=datos.get('tipo_presupuesto'),
        monto_presupuesto=float(datos.get('monto_presupuesto', 0)),
        evento_cobro=datos.get('evento_cobro'),
        objetivos=datos.get('objetivos'),
        edad_min=datos.get('edad_min'),
        edad_max=datos.get('edad_max'),
        genero=datos.get('genero'),
        ubicaciones=datos.get('ubicaciones'),
        intereses=datos.get('intereses'),
        estado=datos.get('estado', 'PAUSADA'),
        fecha_inicio=datos.get('fecha_inicio'),
        fecha_fin=datos.get('fecha_fin'),
        usuario=request.user
    )
    campana.save()
    return campana

# def validar_requisitos_facebook(datos):
#     return {'valido': True, 'datos_validados': datos}
