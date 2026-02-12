from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from . import views

app_name = "system"
urlpatterns = [
    # 这里放业务应用自己的 urlpatterns
    # path("digishow/", include('digishow.urls')),
    # path("lgtools/", include('lgtools.urls')),
    # path('9type/', include('ninetype.urls')),
    # path('medicord/', include('medicord.urls')),
    # path('articalagent/', include('articalagent.urls')),
    # path('stocommando/', include('stocommando.urls')),
    # 业务应用自己的 urlpatterns 结束
    
    path("admin-site/", admin.site.urls),
    path("secretary/", include('secretary.urls')),
    # 下面是system应用自己的view
    path('system/auth/mocklogin', views.MockLoginView.as_view()),
    path("system/auth/wxAuthLogin", views.WechatAuthLoginView.as_view()),
    path("system/auth/wxLogin", views.WxMiniprogramLoginView.as_view()),
    path("system/auth/smslogin", views.SMSLoginView.as_view()),
    path("system/auth/login", views.UsernamePasswordLoginView.as_view()),
    path("system/auth/logout", views.LogoutView.as_view()),
    path("system/auth/refresh", views.RefreshTokenView.as_view()),
    path('system/auth/token/obtain', TokenObtainPairView.as_view()),
    path('system/auth/token/refresh', TokenRefreshView.as_view()),
    path('system/auth/token/verify', TokenVerifyView.as_view()),

    path('system/wxjsdk/config', views.WxJsdkConfigView.as_view()),
    path('wxpay/notify', views.OrderPayNotifyFromWechatView.as_view()),

    path('system/menu/list', views.SysMenuListView.as_view()),
    # path('system/user/recharge', views.UserRechargeView.as_view()),
    path('system/modelscope/token', views.ModelscopeTokenView.as_view()),
]