from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from secretary.agent.secretary import memory as secretary_memory


class UserMemoryView(APIView):
    # permission_classes = [IsAdminUser]
    def get(self, request: Request, user: str) -> Response:
        # user 是微信用户的openid
        
        return Response(secretary_memory.state_dict())


