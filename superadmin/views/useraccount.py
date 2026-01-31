from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from system.infra.common.result import page_success, success, error
from superadmin.models import UserManageAccount


class UserPrivilegeView(APIView):
    ''' 用户的功能权限 '''
    def get(self, request: Request) -> Response:
        pass


class UserListQueryView(APIView):
    permission_classes = [IsAdminUser]
    ''' 用户列表查询 '''
    def get(self, request: Request) -> Response:
        pageNum = request.query_params.get('pageNum') or 1
        pageSize = request.query_params.get('pageSize') or 10
        query = UserManageAccount.objects.all().order_by('-register_time')
        total = query.count()
        
        data = [{
            'id': i.user.pk,
            'username': i.user.username,
            'nickname': i.nickname,
            'email': i.user.email,
            'balance': i.balance,
            'level': i.level,
            'registerTime': i.register_time,
            'status': i.user.is_active,
        } for i in Paginator(query, pageSize).get_page(pageNum)]

        return page_success(data, total)

    def delete(self, request: Request) -> Response:
        ''' 批量删除用户 '''
        pass


class UserDetailsView(APIView):
    # authentication_classes = []
    permission_classes = [IsAdminUser]
    ''' 用户详情 '''
    def get(self, request: Request, user_id: int) -> Response:
        UserManageAccount.objects.filter(user_id=user_id).get()
        return success()

    def post(self, request: Request) -> Response:
        ''' 新增用户 '''
        username = request.data.get('username')
        balence = request.data.get('balance') if request.data.get('balance') else 0
        level = request.data.get('level') if request.data.get('level') else 0
        user = User.objects.create_user(username, f"{username}@linkgeeks.com.cn", "123456")
        UserManageAccount.objects.create(user_id=user.pk, balance=balence, level=level)
        return success()

    def put(self, request: Request, user_id: int) -> Response:
        ''' 修改用户信息 '''
        username = request.data.get('username')
        balence = request.data.get('balance') if request.data.get('balance') else 0
        level = request.data.get('level') if request.data.get('level') else 0
        user_account = UserManageAccount.objects.get(user__id=user_id)
        user_account.user.username = username
        user_account.balance = balence
        user_account.level = level
        user_account.save()
        user_account.user.save()
        return success()

    def delete(self, request: Request, user_id: int) -> Response:
        ''' 删除用户 '''
        User.objects.filter(id=user_id).delete()
        return success()


