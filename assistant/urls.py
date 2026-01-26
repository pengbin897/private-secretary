from django.urls import path

from .views import *

urlpatterns = [
    path("wxmp_request_forward", wxmp_request_forward)
]
