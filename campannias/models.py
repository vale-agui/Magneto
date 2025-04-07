from django.db import models

class CredencialAPI_google(models.Model):
    refresh_token = models.TextField()
    access_token = models.TextField(blank=True, null=True)
    expires_in = models.IntegerField(blank=True, null=True)
    token_type = models.CharField(max_length=50, blank=True, null=True)
    scope = models.CharField(max_length=300, blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Credencial creada el {self.creado}"