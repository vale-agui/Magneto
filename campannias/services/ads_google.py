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

# Configuración de credenciales simuladas
MOCK_CREDENTIALS = {
    "developer_token": "mock_developer_token",
    "client_id": "mock_client_id",
    "client_secret": "mock_client_secret",
    "refresh_token": "mock_refresh_token",
    "access_token": "mock_access_token",
    "token_expiry": (datetime.now() + timedelta(hours=1)).isoformat()
}

# Clientes simulados
MOCK_CLIENTS = [
    {
        "id": "123456789",
        "name": "Cliente Ejemplo 1",
        "currency_code": "MXN",
        "time_zone": "America/Mexico_City"
    },
    {
        "id": "987654321",
        "name": "Cliente Ejemplo 2",
        "currency_code": "MXN",
        "time_zone": "America/Mexico_City"
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
    Actualmente la validación está comentada; ajusta según requieras.
    """
    image = Image.open(django_file)
    ancho, alto = image.size
    # Ejemplo de validación:
    # if tipo == "cuadrada" and (ancho < 300 or alto < 300 or ancho != alto):
    #     return False, "La imagen cuadrada debe ser al menos 300x300 píxeles y tener relación 1:1"
    # if tipo == "horizontal" and (ancho < 600 or alto < 314 or round(ancho / alto, 2) != 1.91):
    #     return False, "La imagen horizontal debe ser al menos 600x314 píxeles y tener relación 1.91:1"
    return True, ""


class GoogleAdsSimulator:
    def __init__(self):
        self.formatos_anuncio = [
            "Texto",
            "Imagen",
            "Video",
            "Responsive",
            "Shopping"
        ]
        
        self.ubicaciones = [
            "Búsqueda de Google",
            "Sitios web asociados",
            "YouTube",
            "Gmail"
        ]

    def simular_creacion_campana(self, datos_campana):
        """
        Simula la creación de una campaña en Google Ads
        """
        return {
            "id_campana": f"g-{random.randint(100000, 999999)}",
            "nombre": datos_campana.get("nombre", "Campaña Google"),
            "estado": "ACTIVA",
            "presupuesto_diario": datos_campana.get("presupuesto", 0) / 30,
            "tipo_campana": random.choice(self.formatos_anuncio),
            "ubicaciones": random.sample(self.ubicaciones, 2),
            "fecha_creacion": datetime.now().isoformat(),
            "metricas_simuladas": {
                "impresiones_estimadas": random.randint(5000, 20000),
                "clics_estimados": random.randint(100, 1000),
                "conversiones_estimadas": random.randint(10, 100),
                "costo_estimado": round(random.uniform(50, 500), 2)
            }
        }

    def simular_preview_anuncio(self, datos_anuncio):
        """
        Simula cómo se vería el anuncio en Google
        """
        return {
            "titulo": datos_anuncio.get("titulo", "Título del Anuncio"),
            "descripcion": datos_anuncio.get("descripcion", "Descripción del anuncio..."),
            "url_destino": datos_anuncio.get("url", "https://ejemplo.com"),
            "formato": random.choice(self.formatos_anuncio),
            "preview_movil": {
                "titulo": "Cómo se ve en móvil",
                "descripcion": "Vista previa en dispositivos móviles"
            },
            "preview_escritorio": {
                "titulo": "Cómo se ve en escritorio",
                "descripcion": "Vista previa en navegadores de escritorio"
            }
        }

    def simular_metricas(self, id_campana):
        """
        Simula las métricas de rendimiento de una campaña
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

def listar_campanas_google(customer_id=None):
    """Simula la obtención de campañas de Google Ads"""
    return MOCK_CAMPAIGNS

def crear_campana_google_ads(request):
    """Simula la creación de una campaña en Google Ads"""
    try:
        data = json.loads(request.body)
        nueva_campana = {
            "id": str(len(MOCK_CAMPAIGNS) + 1),
            "name": data.get("nombre"),
            "status": "ENABLED",
            "budget": float(data.get("presupuesto_diario", 0)),
            "start_date": data.get("fecha_inicio"),
            "end_date": data.get("fecha_fin")
        }
        MOCK_CAMPAIGNS.append(nueva_campana)
        return nueva_campana
    except Exception as e:
        return {"error": str(e)}

def preview_anuncio_google(campania):
    """Simula la vista previa de un anuncio"""
    return {
        "titulo": f"Vista previa de {campania.nombre}",
        "descripcion": "Esta es una vista previa simulada",
        "url_destino": "https://ejemplo.com",
        "imagen": "https://via.placeholder.com/300x200"
    }

def obtener_metricas_google(campania):
    """Simula la obtención de métricas de una campaña"""
    return {
        "impresiones": random.randint(1000, 10000),
        "clicks": random.randint(100, 1000),
        "costo": round(random.uniform(100, 1000), 2),
        "conversiones": random.randint(10, 100)
    }

def listar_campanas_google(customer_id="2454952399"):
    """
    Lista las campañas de Google Ads para el customer_id dado.
    Se retorna un JsonResponse con la lista de campañas o con error.
    """
    try:
        ga_service = CLIENT.get_service("GoogleAdsService")
        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
        """
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        resultados = []
        for batch in response:
            for row in batch.results:
                resultados.append({
                    "id": row.campaign.id,
                    "nombre": row.campaign.name,
                    "estado": row.campaign.status.name
                })
        return resultados
    except Exception as e:
        return {"error": str(e)}


def listar_clientes_ads(customer_id="2454952399"):
    """
    Lista los clientes disponibles (o cuentas hijas) para el customer_id.
    """
    try:
        ga_service = CLIENT.get_service("GoogleAdsService")
        query = """
            SELECT customer.id, customer.descriptive_name
            FROM customer
        """
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        resultados = []
        for batch in response:
            for row in batch.results:
                resultados.append({
                    "id": row.customer.id,
                    "nombre": row.customer.descriptive_name
                })
        return resultados

    except Exception as e:
        return {"error": str(e)}
