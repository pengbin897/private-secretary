import os

from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'superadmin'
    path = os.path.dirname(os.path.abspath(__file__))