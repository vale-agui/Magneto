from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from ..models import CampanaFacebook, CampanaInstagram, CampanaGoogle
from .ads_google import guardar_campana_google
from .ads_facebook import guardar_campana_facebook 
from .ads_instagram import guardar_campana_instagram
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def seleccionar_redes(request):
    """
    Procesa la selección de redes sociales para la creación de campañas.
    """
    if request.method == 'POST':
        redes = request.POST.getlist('redes')
        if not redes:
            messages.error(request, 'Debes seleccionar al menos una red social.')
            return redirect('campannias:index')
        request.session['redes_seleccionadas'] = redes
        # Redirigir usando GET para iniciar el flujo correctamente
        return redirect(f"{reverse('campannias:crear_campania_dinamica')}?paso=0")
    return redirect('campannias:index')

def crear_campania_dinamica(request):
    """
    Maneja la creación dinámica de campañas en múltiples redes sociales.
    """
    redes = request.session.get('redes_seleccionadas', [])
    paso = int(request.GET.get('paso', 0))  # Inicia en 0

    if request.GET.get('reset') == '1':
        _limpiar_sesion(request)
        return redirect('campannias:index')

    if not redes:
        return redirect('campannias:index')

    if request.method == 'POST' and 'nombre' in request.POST:
        reutilizar = request.POST.get('reutilizar_datos') == 'on'
        campos_comunes = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'presupuesto_diario']
        datos_comunes = {k: request.POST.get(k, '') for k in campos_comunes}
        if reutilizar:
            request.session['datos_comunes'] = datos_comunes
        else:
            request.session['datos_comunes'] = {}

        datos_red = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken' and k != 'reutilizar_datos'}
        red_actual = redes[paso]
        request.session[f'datos_{red_actual}'] = datos_red

        # Si hay más formularios por mostrar
        if paso + 1 < len(redes):
            return redirect(f"{reverse('campannias:crear_campania_dinamica')}?paso={paso+1}")
        else:
            # Ya es el último formulario, guardar todas las campañas
            datos_comunes = request.session.get('datos_comunes', {})
            resultado = _guardar_campanias(request, datos_comunes)
            if resultado is True:
                return render(request, 'campannias/crear_campania_dinamica.html', {
                    'finalizado': True,
                    'mensaje': '¡Campañas creadas exitosamente!'
                })
            elif resultado is False:
                return render(request, 'campannias/crear_campania_dinamica.html', {
                    'error': 'Ocurrieron errores al crear las campañas. Revisa los mensajes.'
                })

    return _mostrar_formulario_actual(request, redes, paso)

def _limpiar_sesion(request):
    """Limpia todos los datos de la sesión relacionados con la creación de campañas."""
    request.session.pop('datos_campania', None)
    request.session.pop('redes_seleccionadas', None)
    request.session.pop('datos_comunes', None)
    for i in range(10):  # Limpia hasta 10 posibles campañas
        request.session.pop(f'datos_campania_{i}', None)

def _guardar_campanias(request, datos_comunes):
    """
    Guarda las campañas en la base de datos según las redes seleccionadas.
    """
    redes_seleccionadas = request.session.get('redes_seleccionadas', [])
    campanias_creadas = []

    for red in redes_seleccionadas:
        datos_red = request.session.get(f'datos_{red}', {})
        # Combinar datos_comunes y datos_red, priorizando datos_red
        datos = {**datos_comunes, **datos_red}

        # Guardar campaña según la red
        if red == 'google':
            campania = guardar_campana_google(request, datos)
        elif red == 'facebook':
            campania = guardar_campana_facebook(request, datos)
        elif red == 'instagram':
            campania = guardar_campana_instagram(request, datos)
        campanias_creadas.append(campania)

    # Limpiar datos de sesión
    _limpiar_sesion(request)

    if campanias_creadas:
        messages.success(request, f"Se crearon {len(campanias_creadas)} campañas exitosamente")
        return True

    return False

def _mostrar_formulario_actual(request, redes, paso):
    """Muestra el formulario correspondiente a la red actual."""
    red_actual = redes[paso]
    template_map = {
        'facebook': 'campannias/crearCampanaFacebook.html',
        'instagram': 'campannias/crearCampanaInstagram.html',
        'google': 'campannias/crearCampanaGoogle.html',
    }
    template = template_map.get(red_actual)
    
    if not template:
        return render(request, 'campannias/crear_campania_dinamica.html', {'error': 'Red social no soportada.'})

    datos_comunes = request.session.get('datos_comunes', {})

    return render(request, template, {
        'paso': paso,
        'total': len(redes),
        'red_actual': red_actual,
        'redes': redes,
        'datos_campania': request.session.get('datos_campania', {}),
        'datos_comunes': datos_comunes,
        # Puedes pasar más datos si tus templates los requieren
    })

def custom_logout(request):
    # Limpia los mensajes pendientes
    list(messages.get_messages(request))
    logout(request)
    return redirect('accounts:login')

def eliminar_campania(request, campania_id):
    """
    Elimina una campaña de cualquier red social.
    Args:
        request: HttpRequest object
        campania_id: ID de la campaña a eliminar
    Returns:
        HttpResponse: Redirección a la lista de campañas
    """
    # Intentar encontrar la campaña en cada modelo
    campania = None
    tipo_campana = None
    
    for model, tipo in [(CampanaGoogle, 'google'), 
                       (CampanaFacebook, 'facebook'), 
                       (CampanaInstagram, 'instagram')]:
        try:
            campania = get_object_or_404(model, id=campania_id, usuario=request.user)
            tipo_campana = tipo
            break
        except:
            continue
    
    if not campania:
        messages.error(request, 'Campaña no encontrada')
        return redirect('campannias:listar_campanias')
    
    try:
        nombre_campania = campania.nombre
        campania.delete()
        messages.success(request, f'Campaña {nombre_campania} eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar la campaña: {str(e)}')
    
    return redirect('campannias:listar_campanias')

@login_required
def eliminar_campana(request, campania_id):
    return eliminar_campania(request, campania_id)
