from google.ads.googleads.client import GoogleAdsClient
from pathlib import Path
from django.http import JsonResponse
from uuid import uuid4
from django.shortcuts import redirect
from google.ads.googleads.errors import GoogleAdsException
from PIL import Image
import datetime

# Cargar configuración de Google Ads
yaml_path = Path(__file__).resolve().parent.parent.parent / "google-ads.yaml"
client = GoogleAdsClient.load_from_storage(str(yaml_path))

def validar_imagen(django_file, tipo="cuadrada"):
    image = Image.open(django_file)
    ancho, alto = image.size
    #if tipo == "cuadrada" and (ancho < 300 or alto < 300 or ancho != alto):
      #  return False, "La imagen cuadrada debe ser al menos 300x300 píxeles y tener relación 1:1"
    #if tipo == "horizontal" and (ancho < 600 or alto < 314 or round(ancho / alto, 2) != 1.91):
    #    return False, "La imagen horizontal debe ser al menos 600x314 píxeles y tener relación 1.91:1"
    return True, ""

def crear_campana_google_ads(request):
    try:
        # Obtener datos del formulario
        nombre = request.POST.get("nombre_campana")
        presupuesto_cop = int(request.POST.get("presupuesto_diario"))
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin", "")
        tipo_red = request.POST.get("tipo_red")
        estrategia_puja = request.POST.get("estrategia_puja")
        titulo = request.POST.get("titulo_anuncio")
        descripcion = request.POST.get("descripcion_anuncio")
        url_destino = request.POST.get("url_destino")
        imagen_cuadrada = request.FILES.get("imagen_cuadrada")
        imagen_horizontal = request.FILES.get("imagen_horizontal")

        # Validación de imágenes
        valida1, error1 = validar_imagen(imagen_cuadrada, "cuadrada")
        valida2, error2 = validar_imagen(imagen_horizontal, "horizontal")
        if not valida1 or not valida2:
            return JsonResponse({"error": error1 or error2}, status=400)

        presupuesto_micros = presupuesto_cop * 1_000_000
        customer_id = "2454952399"

        # Crear presupuesto
        budget_service = client.get_service("CampaignBudgetService")
        budget_operation = client.get_type("CampaignBudgetOperation")
        budget = budget_operation.create
        budget.name = f"Presupuesto {nombre} - {uuid4().hex[:6]}"
        budget.amount_micros = presupuesto_micros
        budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        budget_response = budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[budget_operation]
        )
        budget_id = budget_response.results[0].resource_name

        # Crear campaña
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = nombre
        campaign.advertising_channel_type = (
            client.enums.AdvertisingChannelTypeEnum.SEARCH
            if tipo_red == "SEARCH" else client.enums.AdvertisingChannelTypeEnum.DISPLAY
        )
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.campaign_budget = budget_id

        # Estrategia de puja dinámica
        if estrategia_puja == "MANUAL_CPC":
            campaign.manual_cpc = client.get_type("ManualCpc")
        elif estrategia_puja == "MAXIMIZE_CLICKS":
            campaign.maximize_clicks = client.get_type("MaximizeClicks")

        campaign.start_date = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").strftime("%Y%m%d")
        if fecha_fin:
            campaign.end_date = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").strftime("%Y%m%d")

        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name

        # Segmentación: idioma y ubicación
        criterion_service = client.get_service("CampaignCriterionService")
        operations = []

        lang = client.get_type("CampaignCriterion")()
        lang.campaign = campaign_resource_name
        lang.language.language_constant = "languageConstants/1000"

        op_lang = client.get_type("CampaignCriterionOperation")()
        op_lang.create = lang

        loc = client.get_type("CampaignCriterion")()
        loc.campaign = campaign_resource_name
        loc.location.geo_target_constant = "geoTargetConstants/2124"

        op_loc = client.get_type("CampaignCriterionOperation")()
        op_loc.create = loc

        criterion_service.mutate_campaign_criteria(
            customer_id=customer_id,
            operations=[op_lang, op_loc]
            )

        if operations:
            criterion_service.mutate_campaign_criteria(customer_id=customer_id, operations=operations)

        # Subir assets (imágenes)
        asset_service = client.get_service("AssetService")
        def subir_asset_imagen(imagen, nombre):
            image_bytes = imagen.read()
            asset_op = client.get_type("AssetOperation")
            asset = asset_op.create
            asset.name = nombre
            asset.type_ = client.enums.AssetTypeEnum.IMAGE
            asset.image_asset.data = image_bytes
            response = asset_service.mutate_assets(customer_id=customer_id, operations=[asset_op])
            return response.results[0].resource_name

        asset_cuadrado = subir_asset_imagen(imagen_cuadrada, f"{nombre}_cuadrada")
        asset_horizontal = subir_asset_imagen(imagen_horizontal, f"{nombre}_horizontal")

        # Grupo de anuncios
        ad_group_service = client.get_service("AdGroupService")
        ad_group_op = client.get_type("AdGroupOperation")
        ad_group = ad_group_op.create
        ad_group.name = f"Grupo {nombre}"
        ad_group.campaign = campaign_resource_name
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group_resp = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_op]
        )
        ad_group_resource = ad_group_resp.results[0].resource_name

        # Crear anuncio
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_op = client.get_type("AdGroupAdOperation")
        ad = ad_op.create
        ad.ad_group = ad_group_resource
        ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
        ad.ad.final_urls.append(url_destino)

        rsa = ad.ad.responsive_display_ad
        rsa.headlines.add().text = titulo
        rsa.descriptions.add().text = descripcion
        rsa.marketing_images.add().asset = asset_horizontal
        rsa.square_marketing_images.add().asset = asset_cuadrado

        ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_op]
        )

        return redirect('campannias:index')

    except GoogleAdsException as ex:
        error_messages = []
        for error in ex.failure.errors:
            error_messages.append({
                "mensaje": error.message,
                "campo": [f.field_name for f in error.location.field_path_elements] if error.location else "N/A",
                "código": error.error_code.__class__.__name__
            })
        return JsonResponse({
            "error": "Error de la API de Google Ads",
            "detalles": error_messages
        }, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
