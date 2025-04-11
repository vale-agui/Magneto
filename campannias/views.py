import os
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.http import JsonResponse
from google.ads.googleads.errors import GoogleAdsException
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path

from .services.ads_google import (
    crear_campana_google_ads,
    listar_campanas_google,
    listar_clientes_ads
)

from .services.ads_facebook import (
    crear_campana_facebook_ads,
    facebook_auth_url,
    facebook_callback_logic,
    listar_cuentas_facebook_service
)

# Importa la lógica para cada plataforma desde el directorio services
from .services.ads_google import crear_campana_google_ads
from .services.ads_facebook import crear_campana_facebook_ads
from .services.ads_instagram import crear_campana_instagram_ads  # Placeholder o implementado

##########################
### VISTAS PARA RENDERIZAR FORMULARIOS
##########################

def index(request):
    # Página de inicio, donde se muestran enlaces para cada plataforma
    return render(request, 'campannias/crearCampana.html')

def crear_google_view(request):
    # Renderiza el formulario para crear campañas en Google Ads
    return render(request, 'campannias/crearCampanaGoogle.html')

def crear_facebook_view(request):
    # Renderiza el formulario para crear campañas en Facebook Ads
    return render(request, 'campannias/crearCampanaFacebook.html')

def crear_instagram_view(request):
    # Renderiza el formulario para crear campañas en Instagram Ads
    return render(request, 'campannias/crearCampanaInstagram.html')


##########################
### VISTAS PARA PROCESAR LAS SOLICITUDES
##########################
def crear_campana_google(request):
    if request.method == "POST":
        try:
            respuesta = crear_campana_google_ads(request)
            # Si la respuesta es un JsonResponse se asume que hubo error
            if isinstance(respuesta, JsonResponse):
                errores = respuesta.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña: {errores}")
            else:
                messages.success(request, "¡Campaña creada exitosamente!")
            return redirect('campannias:crear_google_view')
        except GoogleAdsException as ex:
            for error in ex.failure.errors:
                mensaje = f"{error.message} (Campo: {getattr(error.location, 'field_path_elements', 'N/A')})"
                messages.error(request, mensaje)
            return redirect('campannias:crear_google_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_google_view')

    return render(request, 'campannias/crearCampanaGoogle.html')


def listar_campanas_google_view(request):
    """
    Vista para listar campañas. La función de servicio retorna un diccionario o una lista.
    En este ejemplo se retorna un JsonResponse.
    """
    resultados = listar_campanas_google()
    if isinstance(resultados, dict) and resultados.get("error"):
        return JsonResponse(resultados, status=500)
    return JsonResponse(resultados, safe=False)


def listar_clientes_ads_view(request):
    """
    Vista para listar clientes (cuentas hijas) de Google Ads.
    """
    resultados = listar_clientes_ads()
    if isinstance(resultados, dict) and resultados.get("error"):
        return JsonResponse(resultados, status=500)
    return JsonResponse(resultados, safe=False)

@csrf_exempt
def crear_campana_facebook(request):
    if request.method == "POST":
        try:
            response = crear_campana_facebook_ads(request)
            if isinstance(response, JsonResponse):
                errores = response.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña Facebook: {errores}")
            else:
                messages.success(request, "¡Campaña Facebook creada exitosamente!")
            return redirect('campannias:crear_facebook_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_facebook_view')
    return render(request, 'campannias/crearCampanaFacebook.html')

def facebook_auth_start(request):
    url, error = facebook_auth_url()
    if error:
        return JsonResponse({"error": error}, status=500)
    return redirect(url)


def facebook_callback(request):
    tokens, error_response = facebook_callback_logic(request)
    if error_response:
        return error_response

    # Guarda el token en la base de datos
    # Asegúrate de haber definido el modelo CredencialAPI_facebook correctamente.
    from campannias.models import CredencialAPI_facebook  # Importa aquí para evitar problemas de import circular
    CredencialAPI_facebook.objects.create(
        access_token=tokens.get("access_token"),
        token_type="bearer",
        expires_in=tokens.get("expires_in"),
        scope="ads_management,business_management"
    )
    return JsonResponse({"mensaje": "Token de Facebook guardado correctamente"})


def listar_cuentas_facebook(request):
    resultado = listar_cuentas_facebook_service()
    if isinstance(resultado, dict) and resultado.get("error"):
        return JsonResponse(resultado, status=400)
    return JsonResponse(resultado, safe=False)


def crear_campana_instagram(request):
    if request.method == "POST":
        try:
            response = crear_campana_instagram_ads(request)  # Función a implementar en ads_instagram.py (placeholder)
            if isinstance(response, JsonResponse):
                errores = response.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña Instagram: {errores}")
            else:
                messages.success(request, "¡Campaña Instagram creada exitosamente!")
            return redirect('campannias:crear_instagram_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_instagram_view')
    return render(request, 'campannias/crearCampanaInstagram.html')


##########################
### OTRAS VISTAS (Google OAuth, token refresh, listados, etc.)
##########################

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
    # Guardamos el token en la base de datos
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
    cred.access_token = nuevo_token.get("access_token")
    cred.expires_in = nuevo_token.get("expires_in")
    cred.token_type = nuevo_token.get("token_type")
    cred.save()
    return JsonResponse({
        "mensaje": "Token actualizado correctamente",
        "access_token": cred.access_token
    })


