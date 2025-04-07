import os
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.http import JsonResponse
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import requests
from .models import CredencialAPI_google
from pathlib import Path


yaml_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
client = GoogleAdsClient.load_from_storage(str(yaml_path))

def index(request):
    return render(request, 'campannias/crearCampana.html')

def crear_campana_google(request):
    if request.method == "POST":
        try:
            yaml_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
            client = GoogleAdsClient.load_from_storage(str(yaml_path))
            ga_service = client.get_service("GoogleAdsService")

            query = """
                SELECT campaign.id, campaign.name
                FROM campaign
            """
            response = ga_service.search_stream(customer_id="2454952399", query=query)

            for batch in response:
                for row in batch.results:
                    print(f"{row.campaign.id} - {row.campaign.name}")

            return redirect('campannias:index')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"mensaje": "Método no permitido"}, status=405)

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

