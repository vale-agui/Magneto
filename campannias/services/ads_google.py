from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.files.uploadedfile import InMemoryUploadedFile
import datetime
from PIL import Image

# Configuración central: se carga el archivo YAML desde la raíz del proyecto (Magneto)
yaml_path = Path(__file__).resolve().parent.parent.parent / "google-ads.yaml"
client = GoogleAdsClient.load_from_storage(str(yaml_path))

# Función para validar dimensiones y proporciones de las imágenes.
def validar_imagen(django_file, tipo="cuadrada"):
    image = Image.open(django_file)
    ancho, alto = image.size
    if tipo == "cuadrada" and (ancho < 300 or alto < 300 or ancho != alto):
        return False, "La imagen cuadrada debe ser al menos 300x300 píxeles y tener relación 1:1"
    if tipo == "horizontal" and (ancho < 600 or alto < 314 or round(ancho / alto, 2) != 1.91):
        return False, "La imagen horizontal debe ser al menos 600x314 píxeles y tener relación 1.91:1"
    return True, ""

def crear_campana_google_ads(request):
    try:
        # --- 1. Obtener datos del formulario ---
        nombre = request.POST.get("nombre_campana")
        presupuesto_cop = int(request.POST.get("presupuesto_diario"))
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin", "")
        tipo_red = request.POST.get("tipo_red")
        # Para el anuncio responsivo se espera tener al menos un título corto y una descripción.
        titulo = request.POST.get("titulo_anuncio")
        descripcion = request.POST.get("descripcion_anuncio")
        url_destino = request.POST.get("url_destino")
        imagen_cuadrada = request.FILES.get("imagen_cuadrada")
        imagen_horizontal = request.FILES.get("imagen_horizontal")
        
        # --- 2. Validar las imágenes ---
        valida1, error1 = validar_imagen(imagen_cuadrada, "cuadrada")
        valida2, error2 = validar_imagen(imagen_horizontal, "horizontal")
        if not valida1 or not valida2:
            return JsonResponse({"error": error1 or error2}, status=400)
        
        # --- 3. Convertir presupuesto de COP a micros ---
        presupuesto_micros = presupuesto_cop * 1_000_000
        
        # --- 4. Cliente ya inicializado globalmente ---
        customer_id = "2454952399"
        
        # --- 5. Crear Presupuesto ---
        budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"Presupuesto {nombre}"
        budget.amount_micros = presupuesto_micros
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget_response = budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_id = budget_response.results[0].resource_name
        
        # --- 6. Crear Campaña ---
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = nombre
        campaign.advertising_channel_type = (
            client.enums.AdvertisingChannelTypeEnum.SEARCH 
            if tipo_red == "SEARCH" 
            else client.enums.AdvertisingChannelTypeEnum.DISPLAY
        )
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.manual_cpc.CopyFrom(client.get_type("ManualCpc"))
        campaign.campaign_budget = budget_id
        campaign.start_date = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
        if fecha_fin:
            campaign.end_date = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name
        
        # --- 7. Agregar Segmentación (Idioma y Ubicación) ---
        # Por defecto se asigna: Español y Colombia; puedes modificar estos valores o capturarlos desde el formulario.
        criterion_service = client.get_service("CampaignCriterionService")
        operations = []
        # Segmentación por idioma (Español)
        language_criterion = client.get_type("CampaignCriterion")
        language_criterion.campaign = campaign_resource_name
        language_criterion.language.language_constant = "languageConstants/1000"  # Español
        op_lang = client.get_type("CampaignCriterionOperation")
        op_lang.create.CopyFrom(language_criterion)
        operations.append(op_lang)
        # Segmentación geográfica (Colombia)
        location_criterion = client.get_type("CampaignCriterion")
        location_criterion.campaign = campaign_resource_name
        location_criterion.location.geo_target_constant = "geoTargetConstants/2124"  # Colombia
        op_loc = client.get_type("CampaignCriterionOperation")
        op_loc.create.CopyFrom(location_criterion)
        operations.append(op_loc)
        if operations:
            criterion_response = criterion_service.mutate_campaign_criteria(
                customer_id=customer_id, operations=operations
            )
        
        # --- 8. Subir imágenes como Assets ---
        asset_service = client.get_service("AssetService")
        def subir_asset_imagen(imagen: InMemoryUploadedFile, asset_nombre: str):
            image_bytes = imagen.read()
            asset_operation = client.get_type("AssetOperation")
            asset = asset_operation.create
            asset.name = asset_nombre
            asset.type_ = client.enums.AssetTypeEnum.IMAGE
            asset.image_asset.data = image_bytes
            response = asset_service.mutate_assets(
                customer_id=customer_id, operations=[asset_operation]
            )
            return response.results[0].resource_name
        
        asset_cuadrado = subir_asset_imagen(imagen_cuadrada, f"{nombre}_cuadrada")
        asset_horizontal = subir_asset_imagen(imagen_horizontal, f"{nombre}_horizontal")
        
        # --- 9. Crear Grupo de Anuncios ---
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = f"Grupo {nombre}"
        ad_group.campaign = campaign_resource_name
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        
        # --- 10. Crear Anuncio de Display Responsivo ---
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad = ad_group_ad_operation.create
        ad.ad_group = ad_group_resource_name
        ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad.ad.final_urls.append(url_destino)
        
        # Para un Responsive Display Ad se recomienda proporcionar múltiples combinaciones;
        # acá se usan los datos básicos (un título y una descripción)
        rsa = ad.ad.responsive_display_ad
        rsa.headlines.add().text = titulo
        rsa.descriptions.add().text = descripcion
        # Asignar imágenes correctamente con el método add()
        marketing_image = rsa.marketing_images.add()
        marketing_image.asset = asset_horizontal
        square_marketing_image = rsa.square_marketing_images.add()
        square_marketing_image.asset = asset_cuadrado
        
        ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        
        return redirect('campannias:index')
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
