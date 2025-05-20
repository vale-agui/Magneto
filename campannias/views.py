import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CampaniaFacebook, CampaniaInstagram, CampaniaGoogle, ResultadoCampania
from .forms import CampaniaFacebookForm, CampaniaInstagramForm, CampaniaGoogleForm
import random
from datetime import timedelta

# Importar servicios
from .services.ads_google import (
    get_auth_url as google_auth_url,
    handle_auth_callback as google_auth_callback,
    refresh_token as google_refresh_token,
    listar_clientes_ads as google_listar_clientes,
    listar_campanas_google as google_listar_campanas,
    crear_campana_google_ads,
    preview_anuncio_google,
    obtener_metricas_google
)

from .services.ads_facebook import (
    facebook_auth_url,
    facebook_callback_logic,
    listar_cuentas_facebook_service,
    crear_campana_facebook_ads,
    preview_anuncio_facebook,
    obtener_metricas_facebook
)

from .services.ads_instagram import (
    crear_campana_instagram_ads,
    preview_anuncio_instagram,
    obtener_metricas_instagram
)

##########################
### VISTAS PARA RENDERIZAR FORMULARIOS
##########################

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

@csrf_exempt
def crear_campana_google(request):
    """Procesa la creación de campañas en Google Ads"""
    if request.method == "POST":
        try:
            respuesta = crear_campana_google_ads(request)
            if isinstance(respuesta, JsonResponse):
                errores = respuesta.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña: {errores}")
            else:
                messages.success(request, "¡Campaña creada exitosamente!")
            return redirect('campannias:crear_google_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_google_view')
    return render(request, 'campannias/crearCampanaGoogle.html')

@csrf_exempt
def crear_campana_facebook(request):
    """Procesa la creación de campañas en Facebook Ads"""
    if request.method == "POST":
        try:
            respuesta = crear_campana_facebook_ads(request)
            if isinstance(respuesta, JsonResponse):
                errores = respuesta.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña Facebook: {errores}")
            else:
                messages.success(request, "¡Campaña Facebook creada exitosamente!")
            return redirect('campannias:crear_facebook_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_facebook_view')
    return render(request, 'campannias/crearCampanaFacebook.html')

@csrf_exempt
def crear_campana_instagram(request):
    """Procesa la creación de campañas en Instagram Ads"""
    if request.method == "POST":
        try:
            respuesta = crear_campana_instagram_ads(request)
            if isinstance(respuesta, JsonResponse):
                errores = respuesta.content.decode('utf-8')
                messages.error(request, f"Error al crear campaña Instagram: {errores}")
            else:
                messages.success(request, "¡Campaña Instagram creada exitosamente!")
            return redirect('campannias:crear_instagram_view')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('campannias:crear_instagram_view')
    return render(request, 'campannias/crearCampanaInstagram.html')

##########################
### VISTAS PARA AUTENTICACIÓN
##########################

def google_auth_start(request):
    """Inicia el proceso de autenticación con Google"""
    url = google_auth_url()
    return redirect(url)

def google_auth_callback(request):
    """Procesa el callback de autenticación de Google"""
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"error": "No code in request"}, status=400)
    
    tokens = google_auth_callback(code)
    return JsonResponse({"mensaje": "Tokens guardados correctamente"})

def facebook_auth_start(request):
    """Inicia el proceso de autenticación con Facebook"""
    url, error = facebook_auth_url()
    if error:
        return JsonResponse({"error": error}, status=500)
    return redirect(url)

def facebook_auth_callback(request):
    """Procesa el callback de autenticación de Facebook"""
    tokens, error_response = facebook_callback_logic(request)
    if error_response:
        return error_response
    return JsonResponse({"mensaje": "Token de Facebook guardado correctamente"})

##########################
### VISTAS PARA LISTADOS Y MÉTRICAS
##########################

def listar_campanas_google_view(request):
    """Lista las campañas de Google Ads"""
    resultados = google_listar_campanas()
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
def preview_anuncio(request, pk):
    """Muestra la vista previa de un anuncio según la plataforma"""
    campania = get_object_or_404(CampaniaGoogle, pk=pk)
    plataforma = request.GET.get('plataforma', 'google')
    
    if plataforma == 'google':
        preview_data = preview_anuncio_google(campania)
    elif plataforma == 'facebook':
        preview_data = preview_anuncio_facebook(campania)
    elif plataforma == 'instagram':
        preview_data = preview_anuncio_instagram(campania)
    else:
        return JsonResponse({'error': 'Plataforma no válida'}, status=400)
    
    return JsonResponse(preview_data)

@login_required
def obtener_metricas(request, pk):
    """Obtiene las métricas de una campaña según la plataforma"""
    campania = get_object_or_404(CampaniaGoogle, pk=pk)
    plataforma = request.GET.get('plataforma', 'google')
    
    if plataforma == 'google':
        metricas = obtener_metricas_google(campania)
    elif plataforma == 'facebook':
        metricas = obtener_metricas_facebook(campania)
    elif plataforma == 'instagram':
        metricas = obtener_metricas_instagram(campania)
    else:
        return JsonResponse({'error': 'Plataforma no válida'}, status=400)
    
    return JsonResponse(metricas)

def listar_campanias(request):
    from .models import CampaniaGoogle
    campanias = CampaniaGoogle.objects.all()
    return render(request, 'campannias/lista_campanias.html', {'campanias': campanias})

def seleccionar_redes(request):
    if request.method == 'POST':
        redes = request.POST.getlist('redes')
        if not redes:
            messages.error(request, 'Debes seleccionar al menos una red social.')
            return redirect('campannias:index')
        request.session['redes_seleccionadas'] = redes
        return redirect('campannias:crear_campania_dinamica')
    return redirect('campannias:index')

def crear_campania_dinamica(request):
    redes = request.session.get('redes_seleccionadas', [])
    datos_campania = request.session.get('datos_campania', {})
    paso = int(request.GET.get('paso', 0))

    # Si el usuario quiere reiniciar el flujo
    if request.GET.get('reset') == '1':
        request.session.pop('datos_campania', None)
        request.session.pop('redes_seleccionadas', None)
        request.session.pop('datos_comunes', None)
        return redirect('campannias:index')

    # Si no hay redes seleccionadas, volver al inicio
    if not redes:
        return redirect('campannias:index')

    # Si se envió el formulario de la red actual, guardar los datos
    if request.method == 'POST':
        reutilizar = request.POST.get('reutilizar_datos') == 'on'
        campos_comunes = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'presupuesto_diario']
        datos_comunes = {k: request.POST.get(k, '') for k in campos_comunes}
        if reutilizar:
            request.session['datos_comunes'] = datos_comunes
        else:
            request.session['datos_comunes'] = {}
        datos_red = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken' and k != 'reutilizar_datos'}
        request.session['datos_campania'] = datos_red
        # Si hay más redes, pasar al siguiente paso
        if paso + 1 < len(redes):
            return redirect(f"{request.path}?paso={paso+1}")
        # Si ya terminó, limpiar sesión y mostrar mensaje de éxito
        request.session.pop('redes_seleccionadas', None)
        request.session.pop('datos_campania', None)
        request.session.pop('datos_comunes', None)
        return render(request, 'campannias/crear_campania_dinamica.html', {'finalizado': True, 'mensaje': '¡Campañas creadas exitosamente!'})

    # Mostrar el formulario correspondiente a la red actual
    red_actual = redes[paso]
    template_map = {
        'facebook': 'campannias/crearCampanaFacebook.html',
        'instagram': 'campannias/crearCampanaInstagram.html',
        'google': 'campannias/crearCampanaGoogle.html',
    }
    form_map = {
        'facebook': CampaniaFacebookForm,
        'instagram': CampaniaInstagramForm,
        'google': CampaniaGoogleForm,
    }
    template = template_map.get(red_actual)
    form_class = form_map.get(red_actual)
    if not template or not form_class:
        return render(request, 'campannias/crear_campania_dinamica.html', {'error': 'Red social no soportada.'})

    datos_comunes = request.session.get('datos_comunes', {})
    form = form_class(initial=datos_comunes)

    return render(request, template, {
        'paso': paso,
        'total': len(redes),
        'red_actual': red_actual,
        'redes': redes,
        'datos_campania': datos_campania,
        'datos_comunes': datos_comunes,
        'form': form,
        'activar_desactivar_url': f"{request.path}?reset=1"
    })


