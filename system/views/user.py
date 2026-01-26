import json
import os
from datetime import datetime
import logging

import time, random
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import jwt
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status

from common.constant import UserChannel
from superadmin.models import UserManageAccount
from system.framework.services import wxmpservice, wxampservice
from superadmin.services import account


logger = logging.getLogger(__name__)

class MockLoginView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = []
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        开发环境模拟登录接口
        返回有效的JWT token，用于后续接口调用
        """
        # 获取或创建一个测试用户
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True
            }
        )
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': '模拟登录成功',
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }) 

class UsernamePasswordLoginView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = []
    ''' 用户名密码登录 '''
    def post(self, request: Request, *args, **kwargs) -> Response:
        # 调用父类的post方法获取token
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        response_data = serializer.validated_data
        response = Response(response_data, status=status.HTTP_200_OK)

        # 设置httpOnly cookie
        response.set_cookie(
            'refresh_token',
            response_data['refresh'],
            httponly=True,
            samesite='Strict',
            secure=True,
        )
        response_data.pop('refresh', None)

        # 更新用户账户的最后登录时间
        user_account = UserManageAccount.objects.filter(user__username=request.data['username']).get()
        user_account.last_login_time = datetime.now()
        user_account.save()

        return response


class RefreshTokenView(TokenRefreshView):
    """自定义Token刷新视图，处理httpOnly cookie的更新"""
    
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        
        # 如果刷新成功且有新的refresh token，更新cookie
        if response.status_code == 200 and hasattr(response, 'data'):
            if 'new_refresh_token' in response.data:
                # 设置新的refresh token到cookie
                response.set_cookie(
                    'refresh_token',
                    response.data['new_refresh_token'],
                    httponly=True,
                    secure=True,
                    samesite='Strict'
                )
                # 从响应中移除new_refresh_token
                response_data = response.data.copy()
                response_data.pop('new_refresh_token', None)
                response.data = response_data
        
        return response


class WechatAuthLoginView(APIView):
    ''' 微信H5授权登录 '''
    authentication_classes = []
    permission_classes = []
    def post(self, request: Request) -> Response:
        code = request.data.get('code')
        state = request.data.get('state')

        if os.environ.get('DEV_MODE'):
            # 模拟的测试用数据
            token_result = {
                'openid': 'k32uaWIaYld',
                "access_token":"ACCESS_TOKEN",
                "expires_in":7200,
                "refresh_token":"REFRESH_TOKEN",
                "scope":"SCOPE",
                "is_snapshotuser": 1,
                "unionid": "UNIONID"
            }
            user_info = {
                "openid": "OPENID",
                'nickname': 'test1',
                "sex": 1,
                "province":"PROVINCE",
                "city":"CITY",
                "country":"COUNTRY",
                "headimgurl":"https://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46",
                "privilege":[ "PRIVILEGE1" "PRIVILEGE2" ],
                "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
            }
        else:
            # 检验是否由平台发起的一个随机串, 这里暂时先把secret写死成小及公众号的
            token_result = wxampservice.oauth_access_token(code)
            if 'errcode' in token_result:
                logger.error(f'获取微信授权失败: {token_result["errmsg"]}')
                return Response({'message': '获取微信授权失败'}, status=401)
            # 获取用户信息
            user_info = wxampservice.get_user_info(token_result['access_token'], token_result['openid'])
            if 'errcode' in user_info:
                logger.error(f'获取微信用户信息失败: {user_info["errmsg"]}')
                return Response({'message': '获取微信用户信息失败'}, status=401)
        
        try:
            # 生成一个随机token
            token = jwt.encode({'access_token': token_result['access_token']}, token_result['openid'])
            unionid = user_info['unionid'] if 'unionid' in user_info else ''
            if UserManageAccount.objects.filter(wx_openid=token_result['openid']).exists():
                user_account = UserManageAccount.objects.filter(wx_openid=token_result['openid']).get()
                user_account.channel = UserChannel.WECHAT_H5
                user_account.wx_unionid = unionid
                user_account.credential = json.dumps(token_result)
                user_account.nickname = user_info['nickname']
                user_account.headimgurl = user_info['headimgurl']
                user_account.last_login_time = datetime.now()
                user_account.token = token
                user_account.save()
                first_login = False
            else:
                # 新用户注册
                user_account = account.register_user(
                    'lguser' + str(user_info['openid']),
                    UserChannel.WECHAT_H5,
                    token,
                    openid=token_result['openid'],
                    unionid=unionid,
                    nickname=user_info['nickname'],
                    headimgurl=user_info['headimgurl'],
                    credential=json.dumps(token_result))
                first_login = True
        except Exception as e:
            logger.error(f'微信授权登录失败: {e}')
            return Response({'message': '微信授权登录失败'}, status=401)
        # 将access_token返回给前端，后续用来做校验
        return Response({
                'id': user_account.user.pk,
                'username': user_account.user.username,
                'token': token,
                'firstLogin': first_login
            })


class WxMiniprogramLoginView(APIView):
    ''' 微信小程序登录 '''
    authentication_classes = []
    permission_classes = []
    def post(self, request: Request) -> Response:
        code = request.query_params.get('code')
        user_state = wxmpservice.get_user_state(code)
        if not user_state:
            return Response({'message': '获取用户状态失败'}, status=401)
        
        # 根据openid+user_state['session_key']生成一个随机token
        token = jwt.encode({'session_key': user_state['session_key']}, user_state['openid'])
        unionid = user_state['unionid'] if 'unionid' in user_state else ''
        if UserManageAccount.objects.filter(wx_openid=user_state['openid']).exists():
            user_account = UserManageAccount.objects.filter(wx_openid=user_state['openid']).get()
            user_account.wx_unionid = unionid
            user_account.last_login_time = datetime.now()
            user_account.credential = json.dumps(user_state)
            user_account.token = token
            user_account.save()
            first_login = False
        else:
            # 先创建系统用户，再创建用户账户
            user_account = account.register_user(
                'lguser' + str(user_state['openid']),
                UserChannel.WECHAT_MINI_PROGRAM,
                token,
                openid=user_state['openid'],
                unionid=unionid,
                nickname=user_state['nickname'],
                credential=json.dumps(user_state))
            first_login = True

        return Response({
                'id': user_account.user.pk,
                'username': user_account.user.username,
                'token': token,
                'firstLogin': first_login
            })


class SMSLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    ''' 短信验证码登录 '''
    def post(self, request: Request) -> Response:
        return Response({'message': 'success'})


class LogoutView(APIView):
    ''' 登出 '''
    authentication_classes = []
    permission_classes = []
    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            # 尝试将refresh token加入黑名单
            refresh_token = request._request.COOKIES.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    # 如果token已经无效，忽略错误
                    pass
            
            # 创建响应并清除cookie
            response = Response({
                'message': '登出成功'
            }, status=status.HTTP_200_OK)
            
            # 删除refresh token cookie
            response.delete_cookie('refresh_token')
            
            return response
            
        except Exception as e:
            return Response({
                'error': '登出过程中发生错误'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRechargeView(APIView):
    ''' 用户充值 '''
    def post(self, request: Request) -> Response:
        user = request.user
        amount = request.data.get('amount')
        user_account = UserManageAccount.objects.filter(user__id=user.id).get()
        if not user_account.wx_openid:
            return Response({'code': 400, 'message': '请先绑定微信'})
        # 根据用户ID、时间戳生成一个随机数的订单编号，尽可能保证唯一
        order_no = f'LGTOOL{int(time.time())}{random.randint(1000, 9999)}'
        # 根据用户判断是公众号还是小程序下单
        if user_account.channel == UserChannel.WECHAT_H5:
            trade = wxampservice.create_pay_order('自助充值', order_no, amount, user_account.wx_openid)
        elif user_account.channel == UserChannel.WECHAT_MINI_PROGRAM:
            trade = wxmpservice.create_pay_order('自助充值', order_no, amount, user_account.wx_openid)
        else:
            return Response({'message': '支付方式错误'}, status.HTTP_400_BAD_REQUEST)
        if not trade:
            return Response({'message': '支付订单创建失败'}, status.HTTP_503_SERVICE_UNAVAILABLE)
        # 记录订单信息
        # UserOrder.objects.create(owner=user, order_no=order_no, amount=amount, trade_no=trade['prepay_id'], payer=user_account.wx_openid)
        return Response(trade)


