# services/ads_facebook.py

import os
from datetime import datetime, timedelta
import random
import json
from django.http import JsonResponse

# Configuración de credenciales simuladas
MOCK_CREDENTIALS = {
    "access_token": "mock_facebook_access_token",
    "app_id": "mock_facebook_app_id",
    "app_secret": "mock_facebook_app_secret",
    "token_expiry": (datetime.now() + timedelta(hours=1)).isoformat()
}

# Cuentas simuladas
MOCK_ACCOUNTS = [
    {
        "id": "act_123456789",
        "name": "Cuenta Facebook 1",
        "currency": "MXN",
        "timezone": "America/Mexico_City"
    },
    {
        "id": "act_987654321",
        "name": "Cuenta Facebook 2",
        "currency": "MXN",
        "timezone": "America/Mexico_City"
    }
]

# Campañas simuladas
MOCK_CAMPAIGNS = [
    {
        "id": "camp_111111111",
        "name": "Campaña Facebook 1",
        "status": "ACTIVE",
        "budget": 100.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    },
    {
        "id": "camp_222222222",
        "name": "Campaña Facebook 2",
        "status": "ACTIVE",
        "budget": 200.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
]

class FacebookAdsSimulator:
    def __init__(self):
        self.formatos_anuncio = [
            "Imagen única",
            "Video",
            "Carrusel",
            "Colección",
            "Historia"
        ]
        
        self.ubicaciones = [
            "Feed de Facebook",
            "Instagram Feed",
            "Historias",
            "Audience Network"
        ]

    def simular_creacion_campana(self, datos_campana):
        """
        Simula la creación de una campaña en Facebook Ads
        """
        return {
            "id_campana": f"fb-{random.randint(100000, 999999)}",
            "nombre": datos_campana.get("nombre", "Campaña Facebook"),
            "estado": "ACTIVA",
            "presupuesto_diario": datos_campana.get("presupuesto", 0) / 30,
            "tipo_campana": random.choice(self.formatos_anuncio),
            "ubicaciones": random.sample(self.ubicaciones, 2),
            "fecha_creacion": datetime.now().isoformat(),
            "metricas_simuladas": {
                "alcance_estimado": random.randint(5000, 20000),
                "impresiones_estimadas": random.randint(10000, 40000),
                "clics_estimados": random.randint(100, 1000),
                "conversiones_estimadas": random.randint(10, 100),
                "costo_estimado": round(random.uniform(50, 500), 2)
            }
        }

    def simular_preview_anuncio(self, datos_anuncio):
        """
        Simula cómo se vería el anuncio en Facebook
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
            "alcance": random.randint(1000, 5000),
            "impresiones": random.randint(2000, 10000),
            "clics": random.randint(50, 200),
            "ctr": round(random.uniform(1, 5), 2),
            "conversiones": random.randint(5, 20),
            "costo_total": round(random.uniform(100, 500), 2),
            "cpa": round(random.uniform(5, 25), 2),
            "roas": round(random.uniform(1, 5), 2)
        }

def facebook_auth_url():
    """Simula la URL de autenticación de Facebook"""
    return "https://www.facebook.com/v18.0/dialog/oauth?mock=true", None

def facebook_callback_logic(request):
    """Simula el manejo del callback de autenticación de Facebook"""
    return MOCK_CREDENTIALS, None

def listar_cuentas_facebook_service():
    """Simula la obtención de cuentas de Facebook Ads"""
    return MOCK_ACCOUNTS

def crear_campana_facebook_ads(request):
    """Simula la creación de una campaña en Facebook Ads"""
    try:
        data = json.loads(request.body)
        nueva_campana = {
            "id": f"camp_{len(MOCK_CAMPAIGNS) + 1}",
            "name": data.get("nombre"),
            "status": "ACTIVE",
            "budget": float(data.get("presupuesto_diario", 0)),
            "start_date": data.get("fecha_inicio"),
            "end_date": data.get("fecha_fin")
        }
        MOCK_CAMPAIGNS.append(nueva_campana)
        return nueva_campana
    except Exception as e:
        return {"error": str(e)}

def preview_anuncio_facebook(campania):
    """Simula la vista previa de un anuncio de Facebook"""
    return {
        "titulo": f"Vista previa de {campania.nombre}",
        "descripcion": "Esta es una vista previa simulada de Facebook",
        "url_destino": "https://ejemplo.com",
        "imagen": "https://via.placeholder.com/300x200"
    }

def obtener_metricas_facebook(campania):
    """Simula la obtención de métricas de una campaña de Facebook"""
    return {
        "alcance": random.randint(1000, 10000),
        "impresiones": random.randint(2000, 20000),
        "clics": random.randint(100, 1000),
        "costo": round(random.uniform(100, 1000), 2),
        "conversiones": random.randint(10, 100)
    }
