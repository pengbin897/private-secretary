from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from system.models import SysMenuSettings, DataModelDict
from system.infra.common.result import page_success, success


class MenuListQueryView(APIView):
    permission_classes = [IsAdminUser]
    ''' 菜单列表查询 '''
    def get(self, request: Request) -> Response:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        query = SysMenuSettings.objects.all()
        total = query.count()
        menus = query.order_by('id').all()

        return page_success(menus, total, page, page_size)


class SysMenuSettingView(APIView):
    permission_classes = [IsAdminUser]
    ''' 后台菜单查看 '''
    def get(self, request: Request) -> Response:
        SysMenuSettings.objects.all()

    def post(self, request: Request) -> Response:
        ...

    def put(self, request: Request) -> Response:
        ...

    def delete(self, request: Request) -> Response:
        ...


class SysDataModelListView(APIView):
    permission_classes = [IsAdminUser]
    ''' 后台数据字典列表 '''
    def get(self, request: Request) -> Response:
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        query = DataModelDict.objects.all()
        total = query.count()
        data = [model_to_dict(d) for d in Paginator(query.order_by('id'), page_size).get_page(page)]

        return page_success(data, total, page, page_size)


class SysDataModelView(APIView):
    def post(self, request: Request) -> Response:
        ''' 新增 '''
        name = request.data.get('name')
        type = request.data.get('type')
        key = request.data.get('key')
        value = request.data.get('value')
        label = request.data.get('label')
        DataModelDict.objects.create(name=name, type=type, key=key, value=value, label=label)
        return success()

    def put(self, request: Request) -> Response:
        ''' 修改 '''
        ...

    def delete(self, request: Request) -> Response:
        ''' 删除 '''
        id = request.query_params.get('id')
        DataModelDict.objects.filter(id=id).delete()
        return success()