import json
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.views.decorators.http import require_POST
from django.http import HttpRequest, HttpResponse

from system.models import UserManageAccount
from system.infra.adaptor.implatform.wechat.wxamp import submit_menu
from secretary.models import UserSchedule, CharacterTracks
from secretary.agent.secretary import load_history_messages, save_history_messages


@require_POST
def submit_menus(request: HttpRequest):
    menu = request.body.decode('utf-8')
    submit_menu(json.loads(menu))
    return HttpResponse(status=200)


class ScheduleQueryView(APIView):
    permission_classes = [IsAdminUser]
    """查询用户日程"""
    def get(self, request: Request) -> Response:
        user_id = request.data.get('user_id', None)
        if not user_id:
            return Response({'message': 'user_id is required'}, status=400)
        
        user = UserManageAccount.objects.get(user_id=user_id)
        if not user:
            return Response({'message': 'user not found'}, status=404)
        
        schedules = UserSchedule.objects.filter(owner=user)
        return Response({'message': 'Hello, World!'})


class UserCharacterView(APIView):
    # permission_classes = [IsAdminUser]
    """查询用户特征"""
    def get(self, request: Request) -> Response:
        user_id = request.data.get('user_id', None)
        if not user_id:
            # 分页查询所有用户特征
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            features = CharacterTracks.objects.all().order_by('owner_id').paginate(page, page_size)
            return Response(features, status=200)
        
        user = UserManageAccount.objects.get(user_id=user_id)
        if not user:
            return Response({'message': 'user not found'}, status=404)
        
        feature = CharacterTracks.objects.get(owner=user)
        return Response({'feature': feature.character_summary})


class UserMessagesView(APIView):
    authentication_classes = []
    permission_classes = []
    # permission_classes = [IsAdminUser]
    """查询用户历史消息"""
    def get(self, request: Request) -> Response:
        user_id = request.data.get('user_id', None)
        if not user_id:
            # 分页查询所有用户历史消息
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('page_size', 10)
            messages = CharacterTracks.objects.all().order_by('owner_id').paginate(page, page_size)
            return Response(messages, status=200)
        
        messages = load_history_messages(user_id)
        return Response(messages, status=200)

    """ 改写 """
    def post(self, request: Request) -> Response:
        user_id = request.data.get('user_id', None)
        if not user_id:
            return Response({'message': 'user_id is required'}, status=400)
        messages = request.data.get('messages', [])
        save_history_messages(user_id, messages)
        return Response(status=200)

