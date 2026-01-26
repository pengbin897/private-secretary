import os

from django.apps import AppConfig

class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assistant'
    path = os.path.dirname(os.path.abspath(__file__))