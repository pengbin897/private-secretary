from django.urls import path

from .views import *

urlpatterns = [
    path("wxmp_request", WxmpRequestView.as_view())
]
