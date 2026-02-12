import time, json
import asyncio, threading
import logging
import xml.etree.ElementTree as ET

from django.http import HttpRequest, HttpResponse
from django.views import View

from system.models import UserManageAccount
from system.infra.adaptor.implatform.wechat.wxamp import send_message_to_user
from secretary.models import UserSchedule
from secretary.agent.secretary import agent_main as secretary_aget


logger = logging.getLogger(__name__)

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
            logger.warning(f"不合法的请求！\n{raw_data}")
            return None

        xmlMsg = ET.fromstring(raw_data)
        # 从请求获取用户的消息内容
        to_user_name = xmlMsg.find('ToUserName').text
        user_openid = xmlMsg.find('FromUserName').text
        create_time = xmlMsg.find('CreateTime').text
        msg_type = xmlMsg.find('MsgType').text
        reply_msg = {
            'ToUserName': user_openid,
            'FromUserName': to_user_name,
            'CreateTime': str(int(time.time())),
            'MsgType': 'text',
            'Content': ''  # 默认回复一个空消息，避免微信公众号提示“该公众号暂时无法提供服务，请稍后再试”
        }
        # 判断用户是否合法用户，再根据用户的功能模式进行对应的处理
        if not UserManageAccount.objects.filter(wx_openid=user_openid).exists():
            reply_msg['Content'] = '您不是合法用户，可以联系法师（CyberMaster119）为您开通使用权限'
            logger.warning(f"用户：\"{user_openid}\" 还不是合法用户")
        else:
            user_id = UserManageAccount.objects.get(wx_openid=user_openid).user.id
            if msg_type == 'event':
                event = xmlMsg.find('Event').text
                logger.info(f"收到公众号后台的事件：{event}")
                # 菜单点击事件
                if event == 'CLICK':
                    menu_key = xmlMsg.find('EventKey').text
                    if menu_key == 'KEY_PROJASSISTANT':
                        # 标书助理
                        reply_msg['Content'] = '已切换为标书助理模式'
                    elif menu_key == 'KEY_SUPERSECRETARY':
                        # 超级秘书
                        reply_msg['Content'] = '已切换为超级秘书模式'
                    else:
                        # 查看所有待办日程的网页
                        pass
            elif msg_type == 'text':
                def reply_hook(reply_content):
                    send_message_to_user(user_openid, reply_content)
                    
                # def handle_wxmessage_async(message_content):
                #     def handle_wxmessage():
                #         loop = asyncio.new_event_loop()
                #         asyncio.set_event_loop(loop)
                #         try:
                #             loop.run_in_executor(None, lambda: secretary_aget(user_id, message_content, reply_hook))
                #         finally:
                #             loop.close()
                #     threading.Thread(target=handle_wxmessage).start()
                # handle_wxmessage_async(xmlMsg.find('Content').text)
                threading.Thread(target=secretary_aget, args=(user_id, xmlMsg.find('Content').text, reply_hook)).start()
            else:
                logger.info(f"收到用户[{user_openid}]的消息：{xmlMsg}")

        return HttpResponse(self.message_to_xml(reply_msg).encode('utf-8'))

    def message_to_xml(self, message: dict):
        # 将message转换成xml格式
        xml_str = '<xml>'
        for k,v in message.items():
            xml_str += f'<{k}>{v}</{k}>'
        xml_str += '</xml>'
        return xml_str


class WxampNotifyUserView(View):
    def post(self, request: HttpRequest, user_id: str) -> HttpResponse:
        message = request.body.decode('utf-8')
        send_message_to_user(user_id, message)
        return HttpResponse(status=200)


# 日程管理相关接口
class UserScheduleListView(View):
    """获取用户所有日程列表"""
    def get(self, request: HttpRequest) -> HttpResponse:
        try:
            # 从请求中获取用户信息（这里假设通过认证中间件或者参数传递）
            user_id = request.GET.get('user_id')
            if not user_id:
                return HttpResponse(
                    json.dumps({'code': 400, 'message': '缺少user_id参数'}, ensure_ascii=False),
                    content_type='application/json',
                    status=400
                )
            
            # 获取用户账户
            try:
                user_account = UserManageAccount.objects.get(user_id=user_id)
            except UserManageAccount.DoesNotExist:
                return HttpResponse(
                    json.dumps({'code': 404, 'message': '用户不存在'}, ensure_ascii=False),
                    content_type='application/json',
                    status=404
                )
            
            # 获取该用户的所有日程，按触发时间排序
            schedules = UserSchedule.objects.filter(owner=user_account).order_by('-fire_time')
            
            # 转换为字典列表
            schedule_list = []
            for schedule in schedules:
                schedule_dict = {
                    'id': schedule.id,
                    'content': schedule.content,
                    'urgency_grade': schedule.urgency_grade,
                    'urgency_grade_display': schedule.get_urgency_grade_display(),
                    'status': schedule.status,
                    'status_display': schedule.get_status_display(),
                    'categories': schedule.categories,
                    'fire_time': schedule.fire_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'record_time': schedule.record_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'create_time': schedule.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_time': schedule.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                schedule_list.append(schedule_dict)
            
            return HttpResponse(
                json.dumps({
                    'code': 200,
                    'message': '成功',
                    'data': {
                        'total': len(schedule_list),
                        'schedules': schedule_list
                    }
                }, ensure_ascii=False),
                content_type='application/json'
            )
        except Exception as e:
            logger.error(f"获取日程列表失败: {str(e)}", exc_info=True)
            return HttpResponse(
                json.dumps({'code': 500, 'message': f'服务器错误: {str(e)}'}, ensure_ascii=False),
                content_type='application/json',
                status=500
            )


class UserScheduleDetailView(View):
    """获取某条日程的详情"""
    def get(self, request: HttpRequest, schedule_id: int) -> HttpResponse:
        try:
            # 从请求中获取用户信息
            user_id = request.GET.get('user_id')
            if not user_id:
                return HttpResponse(
                    json.dumps({'code': 400, 'message': '缺少user_id参数'}, ensure_ascii=False),
                    content_type='application/json',
                    status=400
                )
            
            # 获取用户账户
            try:
                user_account = UserManageAccount.objects.get(user_id=user_id)
            except UserManageAccount.DoesNotExist:
                return HttpResponse(
                    json.dumps({'code': 404, 'message': '用户不存在'}, ensure_ascii=False),
                    content_type='application/json',
                    status=404
                )
            
            # 获取指定的日程（确保是该用户的日程）
            try:
                schedule = UserSchedule.objects.get(id=schedule_id, owner=user_account)
            except UserSchedule.DoesNotExist:
                return HttpResponse(
                    json.dumps({'code': 404, 'message': '日程不存在或无权访问'}, ensure_ascii=False),
                    content_type='application/json',
                    status=404
                )
            
            # 转换为字典
            schedule_dict = {
                'id': schedule.id,
                'content': schedule.content,
                'urgency_grade': schedule.urgency_grade,
                'urgency_grade_display': schedule.get_urgency_grade_display(),
                'status': schedule.status,
                'status_display': schedule.get_status_display(),
                'categories': schedule.categories,
                'fire_time': schedule.fire_time.strftime('%Y-%m-%d %H:%M:%S'),
                'record_time': schedule.record_time.strftime('%Y-%m-%d %H:%M:%S'),
                'create_time': schedule.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': schedule.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'owner': user_account.user.username,
            }
            
            return HttpResponse(
                json.dumps({
                    'code': 200,
                    'message': '成功',
                    'data': schedule_dict
                }, ensure_ascii=False),
                content_type='application/json'
            )
        except Exception as e:
            logger.error(f"获取日程详情失败: {str(e)}", exc_info=True)
            return HttpResponse(
                json.dumps({'code': 500, 'message': f'服务器错误: {str(e)}'}, ensure_ascii=False),
                content_type='application/json',
                status=500
            )


class UserScheduleDeleteView(View):
    """删除用户的某个日程"""
    def delete(self, request: HttpRequest, schedule_id: int) -> HttpResponse:
        try:
            # 从请求中获取用户信息
            user_id = request.GET.get('user_id')
            if not user_id:
                return HttpResponse(
                    json.dumps({'code': 400, 'message': '缺少user_id参数'}, ensure_ascii=False),
                    content_type='application/json',
                    status=400
                )
            
            # 获取用户账户
            try:
                user_account = UserManageAccount.objects.get(user_id=user_id)
            except UserManageAccount.DoesNotExist:
                return HttpResponse(
                    json.dumps({'code': 404, 'message': '用户不存在'}, ensure_ascii=False),
                    content_type='application/json',
                    status=404
                )
            
            # 获取指定的日程（确保是该用户的日程）
            try:
                schedule = UserSchedule.objects.get(id=schedule_id, owner=user_account)
            except UserSchedule.DoesNotExist:
                return HttpResponse(
                    json.dumps({'code': 404, 'message': '日程不存在或无权删除'}, ensure_ascii=False),
                    content_type='application/json',
                    status=404
                )
            
            # 删除日程
            schedule.delete()
            
            return HttpResponse(
                json.dumps({
                    'code': 200,
                    'message': '删除成功'
                }, ensure_ascii=False),
                content_type='application/json'
            )
        except Exception as e:
            logger.error(f"删除日程失败: {str(e)}", exc_info=True)
            return HttpResponse(
                json.dumps({'code': 500, 'message': f'服务器错误: {str(e)}'}, ensure_ascii=False),
                content_type='application/json',
                status=500
            )

