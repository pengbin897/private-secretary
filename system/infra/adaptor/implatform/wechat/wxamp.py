''' 微信公众号后台相关 API '''
import os, requests, logging
import json


logger = logging.getLogger(__name__)

appid = os.environ.get('WECHAT_APPID')
appsecret = os.environ.get('WECHAT_APPSECRET')
# 公众号获取调用凭证
def acquire_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin access token failed, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('access_token')

# 主动给用户发送消息
def send_message_to_user(openid, message_content):
    access_token = acquire_access_token()

    # 构造客服消息发送请求
    request_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    data = {
        "touser": openid,
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    # print(data)
    response = requests.post(request_url, data=bytes(json.dumps(data, ensure_ascii=False), encoding="utf-8"))
    # print(response.json())

# 修改菜单
def submit_menu(menu):
    access_token = acquire_access_token()
    request_url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    response = requests.post(request_url, data=bytes(json.dumps(menu, ensure_ascii=False), encoding="utf-8"))
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'submit weixin menu failed, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json()
