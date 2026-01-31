from django.urls import path

from .views import *

urlpatterns = [
    path("wxamp_request", WxampRequestView.as_view()),
    path("wxamp_notify/<str:user_id>", WxampNotifyUserView.as_view()),
    path("submit_menus", submit_menus),
]
