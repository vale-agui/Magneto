# services/ads_facebook.py

import os
from pathlib import Path
import requests
from django.http import JsonResponse
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User
from dotenv import load_dotenv

# Importa el modelo que almacena los tokens de Facebook
from campannias.models import CredencialAPI_facebook


def crear_campana_facebook_ads(request):
    """
    Simula la creación de una campaña en Facebook Ads.
    Obtiene el token guardado en la BD y utiliza los datos definidos para crear (o validar) una campaña.
    """
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"mensaje": "Método no permitido"}, status=405)

    try:
        # Obtiene el token desde la BD
        cred = CredencialAPI_facebook.objects.latest('creado')
        token = cred.access_token
    except CredencialAPI_facebook.DoesNotExist:
        return JsonResponse({"error": "No hay token de Facebook guardado"}, status=404)

    try:
        # Inicializa la API de Facebook
        FacebookAdsApi.init(
            access_token=token,
            app_id=os.environ.get("FACEBOOK_APP_ID"),
            app_secret=os.environ.get("FACEBOOK_APP_SECRET")
        )

        # Se utiliza el ID de cuenta de anuncios definido en las variables de entorno
        ad_account = AdAccount(os.environ.get("FACEBOOK_AD_ACCOUNT_ID"))

        campaign = ad_account.create_campaign(params={
            'name': 'Campaña de prueba desde Django',
            'objective': 'LINK_CLICKS',
            'status': 'PAUSED',
            'special_ad_categories': [],
            'execution_options': ['VALIDATE_ONLY']  # Solo se valida, no se crea en realidad
        })

        return {
            "mensaje": "Validación exitosa: la campaña se podría crear.",
            "datos_simulados": campaign
        }

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def facebook_auth_url():
    """
    Construye la URL para iniciar el proceso OAuth con Facebook.
    Retorna una tupla (url, error), donde error es None si todo está bien.
    """
    # Cargar variables de entorno desde el archivo .env (ajusta la ruta según tu proyecto)
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI")
    client_id = os.getenv("FACEBOOK_APP_ID")
    scope = "ads_management,business_management"

    if not redirect_uri or not client_id:
        return None, "Variables de entorno no definidas"

    url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"
    )
    return url, None


def facebook_callback_logic(request):
    """
    Procesa el callback de Facebook: obtiene el código, lo intercambia por token y lo retorna.
    En caso de error retorna un JsonResponse de error.
    """
    code = request.GET.get('code')
    if not code:
        return None, JsonResponse({"error": "No se recibió código de autorización"}, status=400)

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    data = {
        "client_id": os.environ.get("FACEBOOK_APP_ID"),
        "client_secret": os.environ.get("FACEBOOK_APP_SECRET"),
        "redirect_uri": os.environ.get("FACEBOOK_REDIRECT_URI"),
        "code": code
    }

    response = requests.get(token_url, params=data)
    if response.status_code != 200:
        return None, JsonResponse({"error": "Error al obtener token", "detalles": response.json()}, status=500)

    tokens = response.json()
    return tokens, None


def listar_cuentas_facebook_service():
    """
    Lista las cuentas de anuncios asociadas al usuario de Facebook.
    Intenta obtener el token desde las variables de entorno (puedes ajustar para obtenerlo de la BD si lo prefieres).
    """
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    if not token:
        return {"error": "Token no encontrado"}

    try:
        FacebookAdsApi.init(access_token=token)
        me = User(fbid='me')
        accounts = me.get_ad_accounts()
        resultado = []
        for account in accounts:
            resultado.append({
                "id": account.get("id"),
                "nombre": account.get("name", "Sin nombre"),
                "estado": account.get("account_status")
            })
        return resultado
    except Exception as e:
        return {"error": str(e)}
