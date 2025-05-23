# services/ads_google.py

import os
from uuid import uuid4
import datetime
from pathlib import Path
from PIL import Image

from django.http import JsonResponse

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from datetime import datetime, timedelta
import random
import json
import time
from django.conf import settings
from ..models import CampanaGoogle

# Configuración de credenciales simuladas según Google Ads API
MOCK_CREDENTIALS = {
    "developer_token": "mock_developer_token",
    "client_id": "mock_client_id",
    "client_secret": "mock_client_secret",
    "refresh_token": "mock_refresh_token",
    "access_token": "mock_access_token",
    "login_customer_id": "1234567890",  # Formato requerido por Google Ads
    "token_expiry": (datetime.now() + timedelta(hours=1)).isoformat(),
    "token_type": "Bearer",
    "api_version": "v15"  # Última versión estable de la API
}

# Clientes simulados según estructura de Google Ads
MOCK_CLIENTS = [
    {
        "id": "1234567890",
        "name": "Cliente Ejemplo 1",
        "currency_code": "MXN",
        "time_zone": "America/Mexico_City",
        "descriptive_name": "Cliente 1 S.A. de C.V.",
        "manager": False,
        "test_account": False,
        "account_type": "STANDARD",
        "auto_tagging_enabled": True,
        "tracking_url_template": None,
        "final_url_suffix": None
    },
    {
        "id": "9876543210",
        "name": "Cliente Ejemplo 2",
        "currency_code": "MXN",
        "time_zone": "America/Mexico_City",
        "descriptive_name": "Cliente 2 S.A. de C.V.",
        "manager": False,
        "test_account": False,
        "account_type": "STANDARD",
        "auto_tagging_enabled": True,
        "tracking_url_template": None,
        "final_url_suffix": None
    }
]

# Campañas simuladas
MOCK_CAMPAIGNS = [
    {
        "id": "111111111",
        "name": "Campaña de Prueba 1",
        "status": "ENABLED",
        "budget": 100.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    {
        "id": "222222222",
        "name": "Campaña de Prueba 2",
        "status": "ENABLED",
        "budget": 200.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
]

def validar_imagen(django_file, tipo="cuadrada"):
    """
    Valida que la imagen cumpla con requisitos de tamaño y proporción.
    """
    image = Image.open(django_file)
    ancho, alto = image.size
    return True, ""

def get_auth_url():
    """Simula la URL de autenticación de Google Ads"""
    return "https://accounts.google.com/o/oauth2/auth?mock=true"

def handle_auth_callback(code):
    """Simula el manejo del callback de autenticación"""
    return MOCK_CREDENTIALS

def refresh_token():
    """Simula la actualización del token"""
    MOCK_CREDENTIALS["access_token"] = "new_mock_access_token"
    MOCK_CREDENTIALS["token_expiry"] = (datetime.now() + timedelta(hours=1)).isoformat()
    return MOCK_CREDENTIALS

def listar_clientes_ads(customer_id=None):
    """Simula la obtención de clientes de Google Ads"""
    return MOCK_CLIENTS

def listar_campanas_google(request):
    """
    Lista las campañas de Google Ads desde la base de datos.
    """
    try:
        campanias = CampanaGoogle.objects.filter(usuario=request.user).order_by('-fecha_creacion')
        resultados = []
        
        for campania in campanias:
            resultados.append({
                "id": campania.id,
                "nombre": campania.nombre,
                "estado": campania.estado,
                "customer_id": campania.customer_id,
                "tipo_campana": campania.tipo_campana,
                "presupuesto_diario": campania.presupuesto_diario,
                "fecha_inicio": campania.fecha_inicio,
                "fecha_fin": campania.fecha_fin,
                "palabras_clave": campania.palabras_clave,
                "ubicaciones": campania.ubicaciones,
                "idiomas": campania.idiomas,
                "puja_maxima": campania.puja_maxima,
                "estrategia_puja": campania.estrategia_puja
            })
        
        return resultados
    except Exception as e:
        return {"error": str(e)}

def guardar_campana_google(request, datos):
    campana = CampanaGoogle(
        nombre=datos.get('nombre'),
        tipo_campana=datos.get('tipo_campana'),
        presupuesto_diario=datos.get('presupuesto_diario'),
        fecha_inicio=datos.get('fecha_inicio'),
        fecha_fin=datos.get('fecha_fin'),
        estado=datos.get('estado', 'PAUSADA'),
        palabras_clave=datos.get('palabras_clave'),
        ubicaciones=datos.get('ubicaciones'),
        idiomas=datos.get('idiomas'),
        puja_maxima=datos.get('puja_maxima'),
        estrategia_puja=datos.get('estrategia_puja'),
        usuario=request.user
    )
    campana.save()
    return campana

# def validar_requisitos_google(datos):
#     return {'valido': True, 'datos_validados': datos}

def simular_metricas(campania):
    """
    Simula las métricas de rendimiento de una campaña de Google Ads.
    Esta función se puede usar para mostrar métricas simuladas de las campañas creadas.
    """
    return {
        "impresiones": random.randint(1000, 5000),
        "clics": random.randint(50, 200),
        "ctr": round(random.uniform(1, 5), 2),
        "conversiones": random.randint(5, 20),
        "costo_total": round(random.uniform(100, 500), 2),
        "cpa": round(random.uniform(5, 25), 2),
        "roas": round(random.uniform(1, 5), 2)
    }
