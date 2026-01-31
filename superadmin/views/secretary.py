from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from secretary.agent.secretary import memory as secretary_memory


class UserMemoryView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request: Request, user: str=None) -> Response:
        # user 是微信用户的openid
        
        return Response(secretary_memory.state_dict())


