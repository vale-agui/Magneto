import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CampanaFacebook, CampanaGoogle, CampanaInstagram, ResultadoCampania
import random
from datetime import timedelta
from django.db.models import Sum

# Importar servicios
from .services.ads_google import (
    listar_clientes_ads as google_listar_clientes,
    listar_campanas_google as google_listar_campanas
)
from .services.ads_facebook import (
    listar_cuentas_facebook_service
)
from .services.ads_instagram import (
    MOCK_CREDENTIALS as instagram_mock_credentials
)


def index(request):
    """Página principal que muestra las opciones de plataformas"""
    return render(request, 'campannias/inicio_campanias.html')

def crear_google_view(request):
    """Renderiza el formulario para crear campañas en Google Ads"""
    return render(request, 'campannias/crearCampanaGoogle.html')

def crear_facebook_view(request):
    """Renderiza el formulario para crear campañas en Facebook Ads"""
    return render(request, 'campannias/crearCampanaFacebook.html')

def crear_instagram_view(request):
    """Renderiza el formulario para crear campañas en Instagram Ads"""
    return render(request, 'campannias/crearCampanaInstagram.html')

##########################
### VISTAS PARA PROCESAR LAS SOLICITUDES
##########################

##########################
### VISTAS PARA LISTADOS Y MÉTRICAS
##########################

def listar_campanas_google_view(request):
    """Lista las campañas de Google Ads"""
    resultados = google_listar_campanas(request)
    if isinstance(resultados, dict) and resultados.get("error"):
        return JsonResponse(resultados, status=500)
    return JsonResponse(resultados, safe=False)

def listar_clientes_ads_view(request):
    """Lista los clientes de Google Ads"""
    resultados = google_listar_clientes()
    if isinstance(resultados, dict) and resultados.get("error"):
        return JsonResponse(resultados, status=500)
    return JsonResponse(resultados, safe=False)

def listar_cuentas_facebook(request):
    """Lista las cuentas de Facebook Ads"""
    resultado = listar_cuentas_facebook_service()
    if isinstance(resultado, dict) and resultado.get("error"):
        return JsonResponse(resultado, status=400)
    return JsonResponse(resultado, safe=False)

@login_required
def listar_campanias(request):
    # Obtener parámetro de red desde la URL
    red = request.GET.get('red')

    # Obtener todas las campañas del usuario actual (ordenadas por fecha)
    campanias_google = CampanaGoogle.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    campanias_facebook = CampanaFacebook.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    campanias_instagram = CampanaInstagram.objects.filter(usuario=request.user).order_by('-fecha_creacion')

    # Pasar todas las campañas al template junto con la red seleccionada
    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram,
        'red': red
    }

    return render(request, 'campannias/lista_campanias.html', context)

def total_gastado(request):
    """Muestra el total gastado en todas las campañas"""
    # Obtener el total gastado por cada tipo de campaña
    total_google = CampanaGoogle.objects.aggregate(total=Sum('presupuesto_diario'))['total'] or 0
    total_facebook = CampanaFacebook.objects.aggregate(total=Sum('monto_presupuesto'))['total'] or 0
    total_instagram = CampanaInstagram.objects.aggregate(total=Sum('presupuesto'))['total'] or 0
    
    # Calcular el total general
    total_general = total_google + total_facebook + total_instagram
    
    context = {
        'total_google': total_google,
        'total_facebook': total_facebook,
        'total_instagram': total_instagram,
        'total_general': total_general
    }
    
    return render(request, 'campannias/total_gastado.html', context)

def costo_por_campania(request):
    """Muestra el costo de cada campaña individual"""
    # Obtener todas las campañas
    campanias_google = CampanaGoogle.objects.all()
    campanias_facebook = CampanaFacebook.objects.all()
    campanias_instagram = CampanaInstagram.objects.all()
    
    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram
    }
    
    return render(request, 'campannias/costo_por_campania.html', context)

@login_required
def reutilizar_campanias(request):
    """Muestra las campañas que pueden ser reutilizadas por red"""
    red = request.GET.get('red')

    campanias_google = CampanaGoogle.objects.filter(estado__in=['ACTIVE'], usuario=request.user)
    campanias_facebook = CampanaFacebook.objects.filter(estado__in=['ACTIVE'], usuario=request.user)
    campanias_instagram = CampanaInstagram.objects.filter(estado__in=['ACTIVE'], usuario=request.user)

    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram,
        'red': red  # Pasamos el valor actual para resaltar el botón seleccionado
    }

    return render(request, 'campannias/reutilizar_campanias.html', context)

@login_required
def detener_campania(request, pk, tipo):
    """Detiene una campaña activa"""
    try:
        if tipo == 'google':
            campania = get_object_or_404(CampanaGoogle, pk=pk, usuario=request.user)
        elif tipo == 'facebook':
            campania = get_object_or_404(CampanaFacebook, pk=pk, usuario=request.user)
        elif tipo == 'instagram':
            campania = get_object_or_404(CampanaInstagram, pk=pk, usuario=request.user)
        else:
            messages.error(request, 'Tipo de campaña no válido')
            return redirect('campannias:listar_campanias')

        if campania.estado == 'ACTIVE':
            campania.estado = 'PAUSED'
            campania.save()
            messages.success(request, f'Campaña {campania.nombre} detenida exitosamente')
        else:
            messages.warning(request, 'Solo se pueden detener campañas activas')

    except Exception as e:
        messages.error(request, f'Error al detener la campaña: {str(e)}')

    return redirect('campannias:listar_campanias')

def actualizar_tokens_view(request):
    """Vista para simular la autenticación y actualización de tokens de cada plataforma."""
    resultado = None
    if request.method == 'POST':
        plataforma = request.POST.get('plataforma')
        if plataforma == 'google':
            from .services.ads_google import refresh_token as google_refresh_token
            creds = google_refresh_token()
            resultado = f"Token de Google Ads actualizado: {creds['access_token']} (expira: {creds['token_expiry']})"
        elif plataforma == 'facebook':
            from .services.ads_facebook import facebook_auth_url
            url, _ = facebook_auth_url()
            resultado = f"Simulación de autenticación de Facebook completada. URL: {url}"
        elif plataforma == 'instagram':
            resultado = f"Token de Instagram Ads simulado: {instagram_mock_credentials['access_token']} (expira: {instagram_mock_credentials['token_expiry']})"
        else:
            resultado = "Plataforma no reconocida."
    return render(request, 'campannias/actualizar_tokens.html', {'resultado': resultado})


