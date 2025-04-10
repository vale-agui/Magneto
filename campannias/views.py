import os
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.http import JsonResponse
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import requests
from .models import CredencialAPI_google
from pathlib import Path
from .services.ads_google import crear_campana_google_ads
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'campannias/crearCampana.html')

#Redirije a la vista de crear campaña de Google Ads
def crear_google_view(request):
    return render(request, 'campannias/crearCampanaGoogle.html')

def crear_campana_google(request):
    if request.method == "POST":
        try:
            response = crear_campana_google_ads(request)
            if isinstance(response, JsonResponse):  # Si hubo error y se devuelve Json
                errores = response.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña: {errores}")
            else:
                messages.success(request, "¡Campaña creada exitosamente!")
            return redirect('campannias:crear_google_view')  # Redirige a la vista del formulario
        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                mensaje = f"{error.message} (Campo: {getattr(error.location, 'field_path_elements', 'N/A')})"
                messages.error(request, mensaje)
            return redirect('campannias:crear_google_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_google_view')

    # Si el método NO es POST, renderiza el formulario
    return render(request, 'campannias/crearCampanaGoogle.html')

def google_auth_start(request):
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "redirect_uri": os.environ["GOOGLE_OAUTH_REDIRECT_URI"],
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/adwords",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{base_url}?{urlencode(params)}"
    return redirect(url)

def oauth2callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "No code in request"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": os.environ["GOOGLE_OAUTH_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to get token", "details": response.json()}, status=500)

    tokens = response.json()

    # ✅ Guardamos en la base de datos
    CredencialAPI_google.objects.create(
        refresh_token=tokens.get("refresh_token"),
        access_token=tokens.get("access_token"),
        expires_in=tokens.get("expires_in"),
        token_type=tokens.get("token_type"),
        scope=tokens.get("scope")
    )

    return JsonResponse({"mensaje": "Tokens guardados correctamente"})

def refrescar_token(request):
    try:
        #  Obtiene el refresh_token más reciente
        cred = CredencialAPI_google.objects.latest('creado')
        refresh_token = cred.refresh_token
    except CredencialAPI_google.DoesNotExist:
        return JsonResponse({"error": "No hay refresh_token guardado"}, status=404)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return JsonResponse({
            "error": "Error al refrescar token",
            "response": response.json()
        }, status=500)

    nuevo_token = response.json()

    # Actualiza la instancia con el nuevo access_token
    cred.access_token = nuevo_token.get("access_token")
    cred.expires_in = nuevo_token.get("expires_in")
    cred.token_type = nuevo_token.get("token_type")
    cred.save()

    return JsonResponse({
        "mensaje": "Token actualizado correctamente",
        "access_token": cred.access_token
    })

def listar_clientes_ads(request):
    try:
        yaml_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
        client = GoogleAdsClient.load_from_storage(str(yaml_path))

        customer_id = "2454952399"  # Puede ser otro si estás usando cuentas hijas

        ga_service = client.get_service("GoogleAdsService")

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

        return JsonResponse(resultados, safe=False)

    except GoogleAdsException as ex:
        return JsonResponse({
            "error": str(ex),
            "detalles": ex.failure.errors[0].message if ex.failure.errors else "Sin detalles"
        }, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def listar_campanas_google(request):
    try:
        yaml_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
        client = GoogleAdsClient.load_from_storage(str(yaml_path))

        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT campaign.id, campaign.name, campaign.status
            FROM campaign
        """

        response = ga_service.search_stream(customer_id="2454952399", query=query)

        resultados = []
        for batch in response:
            for row in batch.results:
                resultados.append({
                    "id": row.campaign.id,
                    "nombre": row.campaign.name,
                    "estado": row.campaign.status.name
                })

        return JsonResponse(resultados, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def crear_campana_facebook(request):
    if request.method not in ["POST", "GET"]:  # GET solo para pruebas
        return JsonResponse({"mensaje": "Método no permitido"}, status=405)

    try:
        # Token desde BD
        cred = CredencialAPI_facebook.objects.latest('creado')
        token = cred.access_token
    except CredencialAPI_facebook.DoesNotExist:
        return JsonResponse({"error": "No hay token de Facebook guardado"}, status=404)

    try:
        FacebookAdsApi.init(
            access_token=token,
            app_id=settings.FACEBOOK_APP_ID,
            app_secret=settings.FACEBOOK_APP_SECRET
        )

        ad_account = AdAccount(settings.FACEBOOK_AD_ACCOUNT_ID)

        campaign = ad_account.create_campaign(params={
            'name': 'Campaña de prueba desde Django',
            'objective': 'LINK_CLICKS',
            'status': 'PAUSED',
            'special_ad_categories': [],
            'execution_options': ['VALIDATE_ONLY']  # 👈 Esto hace que no se cree en realidad
        })

        return JsonResponse({
            "mensaje": "Validación exitosa: la campaña se podría crear.",
            "datos_simulados": campaign
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def facebook_auth_start(request):
    dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path)

    print("DEBUG LOADING .env FROM:", dotenv_path)
    print("DEBUG EXISTS:", dotenv_path.exists())
    print("DEBUG APP_ID:", os.getenv("FACEBOOK_APP_ID"))
    print("DEBUG REDIRECT_URI:", os.getenv("FACEBOOK_REDIRECT_URI"))

    redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI")
    client_id = os.getenv("FACEBOOK_APP_ID")
    scope = "ads_management,business_management"

    if not redirect_uri or not client_id:
        return JsonResponse({"error": "Variables de entorno no definidas"}, status=500)

    url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"
    )
    return redirect(url)

def facebook_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "No se recibió código de autorización"}, status=400)

    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    data = {
        "client_id": os.environ["FACEBOOK_APP_ID"],
        "client_secret": os.environ["FACEBOOK_APP_SECRET"],
        "redirect_uri": os.environ["FACEBOOK_REDIRECT_URI"],
        "code": code
    }

    response = requests.get(token_url, params=data)
    if response.status_code != 200:
        return JsonResponse({"error": "Error al obtener token", "detalles": response.json()}, status=500)

    tokens = response.json()

    # Guardar el token en la base de datos
    CredencialAPI_facebook.objects.create(
        access_token=tokens.get("access_token"),
        token_type="bearer",
        expires_in=tokens.get("expires_in"),
        scope="ads_management,business_management"
    )

    return JsonResponse({"mensaje": "Token de Facebook guardado correctamente"})


def listar_cuentas_facebook(request):
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if not token:
        return JsonResponse({"error": "Token no encontrado"}, status=400)

    try:
        FacebookAdsApi.init(access_token=token)
        me = User(fbid='me')
        accounts = me.get_ad_accounts()

        resultado = []
        for account in accounts:
            resultado.append({
                "id": account["id"],
                "nombre": account.get("name", "Sin nombre"),
                "estado": account.get("account_status")
            })

        return JsonResponse(resultado, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)