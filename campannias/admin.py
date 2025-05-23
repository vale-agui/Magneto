from django.contrib import admin
from .models import CampanaFacebook, CampanaInstagram, CampanaGoogle, ResultadoCampania

admin.site.register(CampanaFacebook)
admin.site.register(CampanaInstagram)
admin.site.register(CampanaGoogle)
admin.site.register(ResultadoCampania)