
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from ..models import UserOrder


class UserOrderQueryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request: Request) -> Response:
        """
        查看用户订单信息
        :param request:
        :return:
        """
        UserOrder.objects.all()
        
        return Response({'code': 200, 'msg': 'success', 'data': []})

