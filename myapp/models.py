from django.contrib.auth.models import User
from django.db import models

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")
    lista_krajów = models.TextField(default="", blank=True)  # Lista wybranych krajówy
    sektory = models.TextField(default="", blank=True)     # Lista sektorów
    kryterium = models.TextField(default="", blank=True)    # Kryteria wyboru