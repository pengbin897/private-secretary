import logging
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import BasePermission

from superadmin.models import UserManageAccount, ToolsConfig


def user_consume_controll(view_func):
    """ 用户消费控制 """
    def wrapped_view(viewcls, request: Request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            # 判断请求的是哪个View
            request_path = request._request.path
            if '/lgtools/cvdreamoving/generate' in request_path:
                cost = ToolsConfig.objects.filter(name=request_path).get().price
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


class AdminMenuPermission(BasePermission):
    def has_permission(self, request, view):
        pass

