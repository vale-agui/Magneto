# services/ads_instagram.py

from django.http import JsonResponse

def crear_campana_instagram_ads(request):
    """
    Simula la creación de una campaña en Instagram Ads.
    Se obtienen los datos enviados a través del formulario y se realizan
    validaciones básicas. En una integración real, aquí se invocaría la API de Instagram.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        # Obtención de datos enviados desde el formulario
        nombre = request.POST.get("nombre")
        presupuesto = request.POST.get("presupuesto")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        objetivo = request.POST.get("objetivo")
        
        # Validaciones básicas: se verifica que ningún campo esté vacío
        if not all([nombre, presupuesto, fecha_inicio, fecha_fin, objetivo]):
            return JsonResponse({"error": "Todos los campos son obligatorios"}, status=400)
        
        # Se podría agregar validación adicional,
        # como que la fecha de inicio sea anterior a la de fin
        
        # Simulación de la creación de la campaña
        print("Simulación de creación de campaña en Instagram Ads:")
        print(f"Nombre: {nombre}")
        print(f"Presupuesto: {presupuesto}")
        print(f"Fecha de inicio: {fecha_inicio}")
        print(f"Fecha de fin: {fecha_fin}")
        print(f"Objetivo: {objetivo}")
        
        # Retorna una respuesta simulada de éxito.
        return {
            "status": "success",
            "mensaje": "Campaña en Instagram creada exitosamente",
            "datos": {
                "nombre": nombre,
                "presupuesto": presupuesto,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "objetivo": objetivo
            }
        }
    
    except Exception as e:
        return JsonResponse({"error": f"Error al crear la campaña: {str(e)}"}, status=500)
