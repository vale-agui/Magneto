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
    # Obtener el parámetro de red de la URL
    red = request.GET.get('red')
    
    # Inicializar las variables de contexto
    context = {
        'red': red,
        'campanias_google': None,
        'campanias_facebook': None,
        'campanias_instagram': None,
        'total_google': 0,
        'total_facebook': 0,
        'total_instagram': 0
    }
    
    # Filtrar campañas según la red seleccionada
    if red == 'google' or not red:
        campanias_google = CampanaGoogle.objects.all()
        total_google = sum(campania.presupuesto_diario or 0 for campania in campanias_google)
        context['campanias_google'] = campanias_google
        context['total_google'] = total_google
    
    if red == 'facebook' or not red:
        campanias_facebook = CampanaFacebook.objects.all()
        total_facebook = sum(campania.monto_presupuesto or 0 for campania in campanias_facebook)
        context['campanias_facebook'] = campanias_facebook
        context['total_facebook'] = total_facebook
    
    if red == 'instagram' or not red:
        campanias_instagram = CampanaInstagram.objects.all()
        total_instagram = sum(campania.presupuesto or 0 for campania in campanias_instagram)
        context['campanias_instagram'] = campanias_instagram
        context['total_instagram'] = total_instagram
    
    return render(request, 'campannias/costo_por_campania.html', context)

@login_required
def reutilizar_campanias(request):
    """Muestra las campañas que pueden ser reutilizadas por red"""
    red = request.GET.get('red')

    # Filtrar campañas activas por red
    campanias_google = CampanaGoogle.objects.filter(estado='ACTIVA', usuario=request.user)
    campanias_facebook = CampanaFacebook.objects.filter(estado='ACTIVA', usuario=request.user)
    campanias_instagram = CampanaInstagram.objects.filter(estado='ACTIVA', usuario=request.user)

    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram,
        'red': red  # Pasamos el valor actual para resaltar el botón seleccionado
    }

    return render(request, 'campannias/reutilizar_campanias.html', context)

@login_required
def detener_campana(request, campania_id):
    # Intentar encontrar la campaña en cada modelo
    campania = None
    for model in [CampanaGoogle, CampanaFacebook, CampanaInstagram]:
        try:
            campania = get_object_or_404(model, id=campania_id, usuario=request.user)
            break
        except:
            continue
    
    if not campania:
        messages.error(request, 'Campaña no encontrada')
        return redirect('campannias:listar_campanias')
    
    if campania.estado == 'ACTIVA':
        campania.estado = 'PAUSADA'
        campania.save()
        messages.success(request, 'Campaña detenida exitosamente')
    else:
        messages.error(request, 'Solo se pueden detener campañas activas')
    
    return redirect('campannias:listar_campanias')

@login_required
def activar_campana(request, campania_id):
    # Intentar encontrar la campaña en cada modelo
    campania = None
    for model in [CampanaGoogle, CampanaFacebook, CampanaInstagram]:
        try:
            campania = get_object_or_404(model, id=campania_id, usuario=request.user)
            break
        except:
            continue
    
    if not campania:
        messages.error(request, 'Campaña no encontrada')
        return redirect('campannias:listar_campanias')
    
    if campania.estado == 'PAUSADA':
        campania.estado = 'ACTIVA'
        campania.save()
        messages.success(request, 'Campaña activada exitosamente')
    else:
        messages.error(request, 'Solo se pueden activar campañas pausadas')
    
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

@login_required
def reutilizar_campana(request, campania_id, tipo):
    """Reutiliza una campaña existente creando una copia con los mismos datos"""
    # Mapeo de tipos de campaña a modelos
    modelos = {
        'google': CampanaGoogle,
        'facebook': CampanaFacebook,
        'instagram': CampanaInstagram
    }
    
    if tipo not in modelos:
        messages.error(request, 'Tipo de campaña no válido')
        return redirect('campannias:reutilizar_campanias')
    
    # Obtener la campaña original
    modelo = modelos[tipo]
    try:
        campania_original = modelo.objects.get(id=campania_id, usuario=request.user)
    except modelo.DoesNotExist:
        messages.error(request, 'Campaña no encontrada')
        return redirect('campannias:reutilizar_campanias')
    
    # Crear una copia de la campaña con los campos base
    campania_nueva = modelo.objects.create(
        usuario=request.user,
        nombre=f"Copia de {campania_original.nombre}",
        estado='ACTIVA',
        fecha_inicio=timezone.now().date(),
        fecha_fin=campania_original.fecha_fin,
    )
    
    # Copiar campos específicos según el tipo de campaña
    if tipo == 'google':
        campania_nueva.presupuesto_diario = campania_original.presupuesto_diario
        campania_nueva.tipo_campana = campania_original.tipo_campana
        campania_nueva.palabras_clave = campania_original.palabras_clave
        campania_nueva.ubicaciones = campania_original.ubicaciones
        campania_nueva.idiomas = campania_original.idiomas
        campania_nueva.puja_maxima = campania_original.puja_maxima
        campania_nueva.estrategia_puja = campania_original.estrategia_puja
    elif tipo == 'facebook':
        campania_nueva.monto_presupuesto = campania_original.monto_presupuesto
        campania_nueva.tipo_presupuesto = campania_original.tipo_presupuesto
        campania_nueva.evento_cobro = campania_original.evento_cobro
        campania_nueva.objetivos = campania_original.objetivos
        campania_nueva.edad_min = campania_original.edad_min
        campania_nueva.edad_max = campania_original.edad_max
        campania_nueva.genero = campania_original.genero
        campania_nueva.ubicaciones = campania_original.ubicaciones
        campania_nueva.intereses = campania_original.intereses
    elif tipo == 'instagram':
        campania_nueva.presupuesto = campania_original.presupuesto
        campania_nueva.image_url = campania_original.image_url
        campania_nueva.caption = campania_original.caption
        campania_nueva.objetivo = campania_original.objetivo
        campania_nueva.tipo_contenido = campania_original.tipo_contenido
        campania_nueva.formato_anuncio = campania_original.formato_anuncio
        campania_nueva.ubicacion_anuncio = campania_original.ubicacion_anuncio
        campania_nueva.edad_min = campania_original.edad_min
        campania_nueva.edad_max = campania_original.edad_max
        campania_nueva.genero = campania_original.genero
        campania_nueva.ubicacion = campania_original.ubicacion
        campania_nueva.intereses = campania_original.intereses
        campania_nueva.hashtags = campania_original.hashtags
    
    campania_nueva.save()
    messages.success(request, 'Campaña reutilizada exitosamente')
    
    # Redirigir a la página de creación de la nueva campaña
    return redirect(f'campannias:crear_{tipo}_view')

@login_required
def dashboard(request):
    """Muestra un dashboard con métricas de las campañas"""
    # Obtener todas las campañas del usuario
    campanias_google = CampanaGoogle.objects.filter(usuario=request.user)
    campanias_facebook = CampanaFacebook.objects.filter(usuario=request.user)
    campanias_instagram = CampanaInstagram.objects.filter(usuario=request.user)
    
    # Simular datos de visualizaciones (en un caso real, estos vendrían de las APIs)
    datos_google = {
        'total_visualizaciones': sum(random.randint(1000, 5000) for _ in campanias_google),
        'total_clics': sum(random.randint(100, 500) for _ in campanias_google),
        'total_conversiones': sum(random.randint(10, 50) for _ in campanias_google),
        'campañas_activas': campanias_google.filter(estado='ACTIVA').count()
    }
    
    datos_facebook = {
        'total_visualizaciones': sum(random.randint(2000, 8000) for _ in campanias_facebook),
        'total_clics': sum(random.randint(200, 800) for _ in campanias_facebook),
        'total_conversiones': sum(random.randint(20, 100) for _ in campanias_facebook),
        'campañas_activas': campanias_facebook.filter(estado='ACTIVA').count()
    }
    
    datos_instagram = {
        'total_visualizaciones': sum(random.randint(3000, 10000) for _ in campanias_instagram),
        'total_clics': sum(random.randint(300, 1000) for _ in campanias_instagram),
        'total_conversiones': sum(random.randint(30, 150) for _ in campanias_instagram),
        'campañas_activas': campanias_instagram.filter(estado='ACTIVA').count()
    }
    
    context = {
        'datos_google': datos_google,
        'datos_facebook': datos_facebook,
        'datos_instagram': datos_instagram,
        'total_visualizaciones': datos_google['total_visualizaciones'] + datos_facebook['total_visualizaciones'] + datos_instagram['total_visualizaciones'],
        'total_clics': datos_google['total_clics'] + datos_facebook['total_clics'] + datos_instagram['total_clics'],
        'total_conversiones': datos_google['total_conversiones'] + datos_facebook['total_conversiones'] + datos_instagram['total_conversiones'],
        'total_campañas_activas': datos_google['campañas_activas'] + datos_facebook['campañas_activas'] + datos_instagram['campañas_activas']
    }
    
    return render(request, 'campannias/dashboard.html', context)


