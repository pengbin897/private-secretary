from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from system.common.result import success, error
from ..models import DataModelDict, SysMenuSettings, SystemSettings


class SysMenuListView(APIView):
    ''' 系统加载菜单 '''    
    def get(self, request: Request) -> Response:
        def _build_menu_tree(menus, parent_id=None):
            """
            构建菜单树形结构
            """
            tree = []
            for menu in menus:
                if menu.parent_id == parent_id:
                    # 构建符合前端接口的菜单项
                    menu_item = {
                        'path': menu.path,
                        'name': menu.name,
                        'component': menu.component,
                        'permission': menu.permission,
                        'meta': {
                            'icon': menu.icon or '',
                            'title': menu.title,
                            'isHide': menu.isHide,
                            'isFull': menu.isFull,
                            'isAffix': menu.isAffix,
                            'isKeepAlive': menu.isKeepAlive,
                        }
                    }
                    # 递归构建子菜单
                    children = _build_menu_tree(menus, menu.id)
                    if children:
                        menu_item['children'] = children
                    tree.append(menu_item)
            return tree
        # 获取所有菜单，按照某种顺序排列（可以根据需要添加排序）
        menus = SysMenuSettings.objects.all().order_by('id')
        # 构建树形结构
        menu_tree = _build_menu_tree(menus)
        return success(menu_tree)


class ModelscopeTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    ''' 阿里modelscope的token '''
    def post(self, request: Request) -> Response:
        token = request.data.get('token')
        if not token:
            return Response('token不能为空', status=status.HTTP_400_BAD_REQUEST)
        SystemSettings.objects.filter(key='MS_TOKEN').update(value=token)
        return Response('token设置成功')


''' 以下是应用端的各种配置获取 '''
class UserStatusSettingView(APIView):
    ''' 用户状态 '''
    def get(self, request: Request) -> Response:
        DataModelDict.objects.filter(key='user_status').all()

    def post(self, request: Request) -> Response:
        ...


class UserLevelSettingView(APIView):
    ''' 用户等级 '''
    def get(self, request: Request) -> Response:
        DataModelDict.objects.filter(key='user_level').all()

    def post(self, request: Request) -> Response:
        ...

