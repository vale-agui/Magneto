import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CampanaFacebook, CampanaGoogle, ResultadoCampania, CampaniaFacebook, CampaniaInstagram, CampaniaGoogle
from .forms import CampaniaFacebookForm, CampaniaInstagramForm, CampaniaGoogleForm
import random
from datetime import timedelta
from django.db.models import Sum

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

@login_required
def crear_campana_google(request):
    """Procesa la creación de campañas en Google Ads"""
    if request.method == 'POST':
        try:
            # Validar requisitos básicos
            if not request.POST.get('customer_id'):
                messages.error(request, 'Se requiere un ID de cliente de Google Ads válido.')
                return render(request, 'campannias/crearCampanaGoogle.html')
            
            if not request.POST.get('developer_token'):
                messages.error(request, 'Se requiere un Developer Token válido.')
                return render(request, 'campannias/crearCampanaGoogle.html')
            
            # Crear nueva campaña
            campana = CampanaGoogle(
                # Campos de autenticación
                customer_id=request.POST['customer_id'],
                developer_token=request.POST['developer_token'],
                refresh_token=request.POST.get('refresh_token', ''),
                access_token=request.POST.get('access_token', ''),
                mcc_account=request.POST.get('mcc_account') == 'on',
                
                # Campos básicos
                nombre=request.POST['nombre'],
                tipo_campana=request.POST['tipo_campana'],
                presupuesto_diario=float(request.POST['presupuesto_diario']),
                fecha_inicio=request.POST['fecha_inicio'],
                fecha_fin=request.POST['fecha_fin'],
                
                # Configuración de segmentación
                palabras_clave=request.POST['palabras_clave'],
                ubicaciones=request.POST['ubicaciones'],
                idiomas=request.POST['idiomas'],
                
                # Configuración de pujas
                puja_maxima=float(request.POST['puja_maxima']),
                estrategia_puja=request.POST['estrategia_puja'],
                
                # Estado y usuario
                estado=request.POST.get('estado', 'PAUSED'),
                usuario=request.user
            )
            
            # Validar tokens de OAuth
            if not campana.refresh_token or not campana.access_token:
                messages.error(request, 'Se requieren tokens de OAuth 2.0 válidos.')
                return render(request, 'campannias/crearCampanaGoogle.html')
            
            # Guardar la campaña
            campana.save()
            
            messages.success(request, 'Campaña de Google Ads creada exitosamente.')
            
            # Si se marcó reutilizar datos, redirigir a la siguiente red
            if request.POST.get('reutilizar_datos'):
                return redirect('campannias:crear_campana_facebook')
            return redirect('campannias:listar_campanias')
            
        except Exception as e:
            messages.error(request, f'Error al crear la campaña: {str(e)}')
            return render(request, 'campannias/crearCampanaGoogle.html')
    
    return render(request, 'campannias/crearCampanaGoogle.html')

@login_required
def crear_campana_facebook(request):
    if request.method == 'POST':
        try:
            # Crear nueva campaña
            campana = CampanaFacebook(
                nombre=request.POST['name'],
                campaign_id=request.POST['campaign_id'],
                tipo_presupuesto=request.POST['budget_type'],
                monto_presupuesto=float(request.POST['budget_amount']) / 100,  # Convertir centavos a dólares
                evento_cobro=request.POST['billing_event'],
                objetivo_optimizacion=request.POST['optimization_goal'],
                edad_min=request.POST['age_min'],
                edad_max=request.POST['age_max'],
                genero=request.POST['gender'],
                ubicaciones=request.POST['locations'],
                intereses=request.POST.get('interests', ''),
                estado=request.POST['status'],
                usuario=request.user
            )
            campana.save()
            
            messages.success(request, 'Campaña de Facebook creada exitosamente.')
            
            # Si se marcó reutilizar datos, redirigir a la siguiente red
            if request.POST.get('reutilizar_datos'):
                return redirect('campannias:crear_campana_instagram')
            return redirect('campannias:listar_campanias')
            
        except Exception as e:
            messages.error(request, f'Error al crear la campaña: {str(e)}')
            return render(request, 'campannias/crearCampanaFacebook.html')
    
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

@login_required
def listar_campanias(request):
    # Obtener todas las campañas de cada red social
    campanias_google = CampanaGoogle.objects.all().order_by('-fecha_creacion')
    campanias_facebook = CampanaFacebook.objects.all().order_by('-fecha_creacion')
    campanias_instagram = CampaniaInstagram.objects.all().order_by('-fecha_creacion')
    
    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram,
    }
    
    return render(request, 'campannias/lista_campanias.html', context)

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

def total_gastado(request):
    """Muestra el total gastado en todas las campañas"""
    # Obtener el total gastado por cada tipo de campaña
    total_google = CampaniaGoogle.objects.aggregate(total=Sum('presupuesto'))['total'] or 0
    total_facebook = CampaniaFacebook.objects.aggregate(total=Sum('presupuesto'))['total'] or 0
    total_instagram = CampaniaInstagram.objects.aggregate(total=Sum('presupuesto'))['total'] or 0
    
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
    campanias_google = CampaniaGoogle.objects.all()
    campanias_facebook = CampaniaFacebook.objects.all()
    campanias_instagram = CampaniaInstagram.objects.all()
    
    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram
    }
    
    return render(request, 'campannias/costo_por_campania.html', context)

def reutilizar_campanias(request):
    """Muestra las campañas que pueden ser reutilizadas"""
    # Obtener campañas finalizadas o exitosas que pueden ser reutilizadas
    campanias_google = CampaniaGoogle.objects.filter(estado__in=['FINALIZADA', 'EXITOSA'])
    campanias_facebook = CampaniaFacebook.objects.filter(estado__in=['FINALIZADA', 'EXITOSA'])
    campanias_instagram = CampaniaInstagram.objects.filter(estado__in=['FINALIZADA', 'EXITOSA'])
    
    context = {
        'campanias_google': campanias_google,
        'campanias_facebook': campanias_facebook,
        'campanias_instagram': campanias_instagram
    }
    
    return render(request, 'campannias/reutilizar_campanias.html', context)


