import time
import logging
import xml.etree.ElementTree as ET

from django.http import HttpRequest, HttpResponse
from django.views import View

from superadmin.models import UserManageAccount
from .wxmsg_handle import WxMsgHandleRunner, send_message


logger = logging.getLogger(__name__)


def message_to_xml(message: dict):
    # 将message转换成xml格式
    xml_str = '<xml>'
    for k,v in message.items():
        xml_str += f'<{k}>{v}</{k}>'
    xml_str += '</xml>'
    return xml_str


class WxampRequestView(View):
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
        if not UserManageAccount.objects.filter(wx_openid=user_id).exists():
            reply_msg['Content'] = '您不是合法用户，可以联系法师（CyberMaster119）为您开通使用权限'
            logging.warning(f"用户：\"{user_id}\" 还不是合法用户")
        else:
            if msg_type == 'event':
                event = xmlMsg.find('Event').text
                logger.info(f"收到公众号后台的事件：{event}")
                # 菜单点击事件
                if event == 'CLICK':
                    event_key = xmlMsg.find('EventKey').text
                    # 查看所有待办日程的网页
                    
            else:
                # print(f"收到用户[{user_id}]的消息：{xmlMsg.find('Content').text}, 回复一个空消息")
                WxMsgHandleRunner(user_id, xmlMsg.find('Content').text).start()

        return HttpResponse(message_to_xml(reply_msg).encode('utf-8'))


class WxampNotifyUserView(View):
    def post(self, request: HttpRequest, user_id: str) -> HttpResponse:
        message = request.body.decode('utf-8')
        send_message(user_id, message)
        return HttpResponse(status=200)
