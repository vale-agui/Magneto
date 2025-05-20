# services/ads_instagram.py

from django.http import JsonResponse
from datetime import datetime
import random

class InstagramAdsSimulator:
    def __init__(self):
        self.objetivos = [
            "Alcance",
            "Tráfico",
            "Conversiones",
            "Instalaciones de aplicaciones",
            "Generación de leads"
        ]
        
        self.ubicaciones = [
            "Feed de Instagram",
            "Historias de Instagram",
            "Reels",
            "Explorar",
            "IGTV"
        ]
        
        self.formatos = [
            "Imagen única",
            "Video",
            "Carrusel",
            "Colección",
            "Reels"
        ]

    def simular_creacion_campana(self, datos_campana):
        """
        Simula la creación de una campaña en Instagram Ads
        """
        return {
            "id_campana": f"ig-{random.randint(100000, 999999)}",
            "nombre": datos_campana.get("nombre", "Campaña Instagram"),
            "estado": "ACTIVA",
            "objetivo": random.choice(self.objetivos),
            "presupuesto_diario": datos_campana.get("presupuesto", 0) / 30,
            "ubicaciones": random.sample(self.ubicaciones, 2),
            "fecha_creacion": datetime.now().isoformat(),
            "metricas_simuladas": {
                "alcance_estimado": random.randint(8000, 40000),
                "impresiones_estimadas": random.randint(12000, 60000),
                "clics_estimados": random.randint(150, 1200),
                "conversiones_estimadas": random.randint(12, 120),
                "costo_estimado": round(random.uniform(60, 600), 2)
            }
        }

    def simular_preview_anuncio(self, datos_anuncio):
        """
        Simula cómo se vería el anuncio en Instagram
        """
        formato = random.choice(self.formatos)
        preview = {
            "titulo": datos_anuncio.get("titulo", "Título del Anuncio"),
            "texto": datos_anuncio.get("texto", "Texto del anuncio..."),
            "url_destino": datos_anuncio.get("url", "https://ejemplo.com"),
            "formato": formato,
            "preview_feed": {
                "titulo": "Vista en Feed de Instagram",
                "descripcion": "Cómo se verá en el feed de Instagram"
            }
        }
        
        if formato == "Carrusel":
            preview["elementos_carrusel"] = [
                {"titulo": f"Elemento {i+1}", "descripcion": f"Descripción {i+1}"}
                for i in range(3)
            ]
        elif formato == "Video":
            preview["duracion_video"] = f"{random.randint(15, 60)} segundos"
        elif formato == "Reels":
            preview["duracion_reel"] = f"{random.randint(15, 30)} segundos"
            preview["musica"] = "Música de fondo simulada"
            
        return preview

    def simular_metricas(self, id_campana):
        """
        Simula las métricas de rendimiento de una campaña
        """
        return {
            "alcance": random.randint(4000, 20000),
            "impresiones": random.randint(6000, 30000),
            "clics": random.randint(75, 600),
            "ctr": round(random.uniform(1, 5), 2),
            "conversiones": random.randint(5, 60),
            "costo_total": round(random.uniform(120, 600), 2),
            "cpa": round(random.uniform(5, 25), 2),
            "roas": round(random.uniform(1, 5), 2)
        }

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
        simulator = InstagramAdsSimulator()
        campana = simulator.simular_creacion_campana({
            "nombre": nombre,
            "presupuesto": presupuesto,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "objetivo": objetivo
        })
        return JsonResponse(campana)
    
    except Exception as e:
        return JsonResponse({"error": f"Error al crear la campaña: {str(e)}"}, status=500)

def preview_anuncio_instagram(request):
    """
    Función para simular la vista previa de un anuncio
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        # Obtención de datos enviados desde el formulario
        titulo = request.POST.get("titulo")
        texto = request.POST.get("texto")
        url = request.POST.get("url")
        
        # Validaciones básicas: se verifica que todos los campos estén presentes
        if not all([titulo, texto, url]):
            return JsonResponse({"error": "Todos los campos son obligatorios"}, status=400)
        
        # Simulación de la vista previa del anuncio
        print("Simulación de vista previa del anuncio en Instagram:")
        print(f"Título: {titulo}")
        print(f"Texto: {texto}")
        print(f"URL: {url}")
        
        # Retorna una respuesta simulada de éxito.
        simulator = InstagramAdsSimulator()
        preview = simulator.simular_preview_anuncio({
            "titulo": titulo,
            "texto": texto,
            "url": url
        })
        return JsonResponse(preview)
    
    except Exception as e:
        return JsonResponse({"error": f"Error al obtener la vista previa del anuncio: {str(e)}"}, status=500)

def obtener_metricas_instagram(request):
    """
    Función para simular las métricas de una campaña
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    
    try:
        # Obtención del ID de la campaña
        id_campana = request.POST.get("id_campana")
        
        # Validación básica: se verifica que el ID esté presente
        if not id_campana:
            return JsonResponse({"error": "El ID de la campaña es obligatorio"}, status=400)
        
        # Simulación de la obtención de métricas
        print(f"Simulación de obtención de métricas de la campaña {id_campana}")
        
        # Retorna una respuesta simulada de éxito.
        simulator = InstagramAdsSimulator()
        metricas = simulator.simular_metricas(id_campana)
        return JsonResponse(metricas)
    
    except Exception as e:
        return JsonResponse({"error": f"Error al obtener las métricas de la campaña: {str(e)}"}, status=500)
