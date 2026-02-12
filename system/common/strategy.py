from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.models import User

from system.models import UserManageAccount


def register_user(
        username: str,
        channel: str,
        token: str,
        password: str='123456',
        openid: str=None,
        unionid: str=None,
        nickname: str=None,
        headimgurl: str=None,
        credential: str=None) -> User:
    ''' 用户首次注册 '''
    user = User.objects.create_user(username=username, password=password)
    account = UserManageAccount.objects.create(
        pk=user.pk,
        wx_openid=openid,
        wx_unionid=unionid,
        user_id=user.pk,
        token=token,
        channel=channel,
        nickname=nickname,
        headimgurl=headimgurl,
        credential=credential,
        balance=50) # 新注册用户赠送50个点

    return account


def user_consume_controll(view_func):
    """ 用户消费控制 """
    def wrapped_view(viewcls, request: Request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            # 判断请求的是哪个View
            # request_path = request._request.path
            # if '/lgtools/cvdreamoving/generate' in request_path:
            #     cost = ToolsConfig.objects.filter(name=request_path).get().price
            balance = UserManageAccount.objects.filter(user=request.user).get().balance
            if balance <= 0:
                # raise Exception('余额不足，请充值', status=403)
                return Response({
                    'errcode': 1,
                    'errmsg': '余额不足，请充值'
                })
            else:
                UserManageAccount.objects.filter(user=request.user).update(balance=balance-1)

        return view_func(viewcls, request, *args, **kwargs)
    return wrapped_view
