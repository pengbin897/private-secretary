import hashlib
import time
import base64

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from system.infra.services import wxjsdkservice, wxmpservice


class WxJsdkConfigView(APIView):
    def post(self, request: Request) -> Response:
        url = request.data.get("url")
        # 将url用base64解密
        real_url = base64.b64decode(url).decode()
        print(f'the real url is {real_url}')
        # 先获取access_token，再获取jsapi_ticket
        access_token = wxmpservice.acquire_access_token()
        jsapi_ticket = wxjsdkservice.get_jsapi_ticket(access_token)

        # 生成签名
        timestamp = int(time.time())
        nonce_str = 'pengbin119'
        string1 = f'jsapi_ticket={jsapi_ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={real_url}'
        signature = hashlib.sha1(string1.encode('utf-8')).hexdigest()
        # 对string1进行sha1加密
        return Response({
            "appid": "wx7c4f191bfc9a1c73",
            "timestamp": timestamp,
            "nonceStr": nonce_str,
            "signature": signature
        })


class OrderPayNotifyFromWechatView(APIView):
    authentication_classes = []
    permission_classes = []
    ''' 微信支付回调 '''
    def post(self, request: Request) -> Response:
        print('收到微信支付回调请求：', request.data)
        # 验证签名

        # 更新订单状态

        # 更新订单中用户的余额
        
        return Response()
