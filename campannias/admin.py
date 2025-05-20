from django.contrib import admin
from .models import CampaniaFacebook, CampaniaInstagram, CampaniaGoogle, ResultadoCampania

admin.site.register(CampaniaFacebook)
admin.site.register(CampaniaInstagram)
admin.site.register(CampaniaGoogle)
admin.site.register(ResultadoCampania)