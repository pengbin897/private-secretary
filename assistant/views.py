import os
import time
import threading
import json
import requests
import logging
import xml.etree.ElementTree as ET

from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.decorators.http import require_POST

from superadmin.models import UserManageAccount
from .agent.main import chat


logger = logging.getLogger(__name__)

class WxPublicAccountService:
    # 获取access_token
    def acquire_access_token(self):
        appid = os.environ.get('WECHAT_APPID')
        secret = os.environ.get('WECHAT_APPSECRET')
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
        response = requests.get(token_url)
        return response.json()["access_token"]

    def handle_wx_message(self, user_id, xml_message ):
        msg_type = xml_message.find('MsgType').text
        if 'event' == msg_type:
            pass
        elif 'text' == msg_type:
            msg_content = xml_message.find('Content').text
            runnable = threading.Thread(target = chat, args=(user_id, msg_content, self.send_message))
            runnable.start()
        else:
            pass
        return None
    
    async def handle_user_message(self, user_id, user_message):
        reply_content = await chat(user_id, user_message)
        self.send_message(user_id, reply_content)


    # 主动给用户发送消息
    def send_message(self, user_id, message):
        access_token = self.acquire_access_token()

        # 构造客服消息发送请求
        request_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        data = {
            "touser": user_id,
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        # print(data)
        response = requests.post(request_url, data=bytes(json.dumps(data, ensure_ascii=False), encoding="utf-8"))
        # print(response.json())


def message_to_xml(message: dict):
    # 将message转换成xml格式
    xml_str = '<xml>'
    for k,v in message.items():
        xml_str += f'<{k}>{v}</{k}>'
    xml_str += '</xml>'
    return xml_str


class WxmpRequestView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        ''' 微信验证 '''
        echostr = request.GET.get("echostr")
        return HttpResponse(echostr)

    def post(self, request: HttpRequest) -> HttpResponse:
        ''' 公众号后台转发过来的消息统一处理中心 '''
        signature = request.GET.get("signature")
        nonce = request.GET.get("nonce")
        timestamp = request.GET.get("timestamp")
        echostr = request.GET.get("echostr")
        openid = request.GET.get("openid")

        # 获取请求body中的数据
        raw_data = request.body.decode('utf-8')
        # 校验是否微信公众号发来的，不是直接拒绝
        if not raw_data or 'xml' not in str(raw_data):
            logger.warning('不合法的请求！')
            return None

        xmlMsg = ET.fromstring(raw_data)
        # 从请求获取用户的消息内容
        to_user_name = xmlMsg.find('ToUserName').text
        user_id = xmlMsg.find('FromUserName').text
        create_time = xmlMsg.find('CreateTime').text
        msg_type = xmlMsg.find('MsgType').text
        reply_msg = {
            'ToUserName': user_id,
            'FromUserName': to_user_name,
            'CreateTime': str(int(time.time())),
            'MsgType': 'text',
            'Content': ''  # 默认回复一个空消息，避免微信公众号提示“该公众号暂时无法提供服务，请稍后再试”
        }
        # 判断用户是否合法用户，再根据用户的功能模式进行对应的处理
        # if not UserManageAccount.objects.filter(wx_openid=user_id).exists():
        #     reply_msg['Content'] = '您不是合法用户，可以联系法师（CyberMaster119）为您开通使用权限'
        #     logging.warning(f"用户：\"{user_id}\" 还不是合法用户")
        # else:
        wxmp_service = WxPublicAccountService()
        if msg_type == 'event':
            event = xmlMsg.find('Event').text
            logger.info(f"收到公众号后台的事件：{event}")
            # 菜单点击事件
            # if event == 'CLICK':
            #     event_key = xmlMsg.find('EventKey').text
            #     userRepo.setUserFeature(user_id, convertFeatureString(event_key))
            #     reply_msg['Content'] = '切换成功'
            #     return HttpResponse(message_to_xml(reply_msg))

        else:
            reply_content = wxmp_service.handle_wx_message(xmlMsg)
            if reply_content:
                reply_msg['Content'] = reply_content

        return HttpResponse(message_to_xml(reply_msg).encode('utf-8'))

