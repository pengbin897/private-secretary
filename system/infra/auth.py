import json
from typing import Set
import logging

from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from system.common.constant import UserChannel
from system.infra.adaptor.implatform.wechat import wxjsdk
from system.models import UserManageAccount


logger = logging.getLogger(__name__)

class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    """从httpOnly cookie中获取refresh token的序列化器，复用TokenRefreshSerializer的所有逻辑"""
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        # 不调用父类的__init__，因为我们需要自定义字段处理
        super(TokenRefreshSerializer, self).__init__(*args, **kwargs)
        # 移除refresh字段，因为我们从cookie获取
        self.fields.pop('refresh', None)
    
    def validate(self, attrs):
        # 从httpOnly cookie中获取refresh token
        refresh_token = self.request.COOKIES.get('refresh_token')
        user_id = self.request.session.get('user_id')
        
        if not refresh_token or not user_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('未找到有效的刷新令牌，请重新登录')
        
        # 只解析一次token，复用refresh对象
        try:
            refresh = RefreshToken(refresh_token)
            if refresh.payload.get('user_id') != user_id:
                from rest_framework.exceptions import ValidationError
                raise ValidationError('令牌验证失败，请重新登录')
        except Exception:
            # 清除无效的session数据
            self.request.session.pop('user_id', None)
            from rest_framework.exceptions import ValidationError
            raise ValidationError('令牌已过期或无效，请重新登录')
        
        # 构造attrs，让父类的validate方法处理token刷新逻辑
        attrs['refresh'] = refresh_token
        
        # 调用父类的validate方法，复用所有token刷新逻辑
        data = super().validate(attrs)
        
        # 如果启用了token轮换，更新cookie中的refresh token
        if 'refresh' in data:
            # 将新的refresh token存储在data中，让视图处理cookie更新
            data['new_refresh_token'] = data['refresh']
            # 从响应中移除refresh token，保持安全
            data.pop('refresh', None)
        
        # 复用之前解析的refresh对象，避免重复解析
        data['expires_in'] = refresh.access_token.lifetime.total_seconds()
        
        return data


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """自定义Token序列化器，添加用户信息"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 可以在这里添加自定义的token声明
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # 添加用户信息到响应中
        data.update({
            'id': self.user.pk,
            'username': self.user.username,
            'token': data['access'],
            'permissions': self.user.get_all_permissions()  # 获取权限列表
        })
        
        return data


class WexinTokenAuthentication(BaseAuthentication):
    """微信公众号和小程序端token验证"""
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', b'').split()
        # if isinstance(auth, str):
        #     # Work around django test client oddness
        #     auth = auth.encode(HTTP_HEADER_ENCODING)
        # auth = auth.split()
        if not auth or auth[0].lower() != 'bearer':
            return None
        
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Credentials string should not contain spaces.')
            raise AuthenticationFailed(msg)

        raw_token = auth[1]
        if raw_token is None:
            return None

        try:
            if not UserManageAccount.objects.filter(token=raw_token).exists():
                logger.warning(f'该token找不到用户记录: {raw_token}')
                return None
            
            user_account = UserManageAccount.objects.filter(token=raw_token).get()
            if user_account.channel == UserChannel.WECHAT_H5.value:
                # 用credential中的access_token去微信进行验证，并获取用户信息
                # print(f'user_account.credential: {user_account.credential}')
                credential = json.loads(user_account.credential)
                if not credential.get('access_token'):
                    return None
                verify_result = wxjsdk.verify_access_token(credential['access_token'], user_account.wx_openid)
                if not verify_result:
                    # 从request cookie中获取refresh_token
                    # refresh_token = request.COOKIES.get('refresh_token')
                    # if not refresh_token:
                    #     print('get refresh token fail')
                    #     raise AuthenticationFailed(
                    #         _("Authorization header must contain two space-delimited values"),
                    #         code="bad_authorization_header",
                    #     )
                    # # 刷新access_token
                    # token_result = wxampservice.refresh_access_token(refresh_token)
                    # access_token = token_result['access_token']
                    # # 更新cookie中的refresh_token
                    # refresh_token = token_result['refresh_token']
                    # request.COOKIES['refresh_token'] = refresh_token
                    return None
            elif user_account.channel == UserChannel.WECHAT_MINI_PROGRAM.value:
                pass # 暂时啥也不用做，能走到这里说明token是有效的
            else:
                # print(f'其他渠道不在这里做验证: {user_account.channel}, {UserChannel.WECHAT_MINI_PROGRAM}')
                # 其他渠道不在这里做验证
                return None

            # user_info = wxampservice.get_user_info(raw_token, user_account.wx_openid)
        except Exception as e:
            logger.warn(f'verify weixin token error, token: {raw_token}, error: {e}')
            return None
        
        return user_account.user, raw_token


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception as e:
            return None

