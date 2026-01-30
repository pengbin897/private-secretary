import threading, asyncio
import os, json, requests
from .agent.main import agent_main


class WxMsgHandleRunner(threading.Thread):
    def __init__(self, user_id, user_content):
        super().__init__()
        self.daemon = True
        self.user_id = user_id
        self.user_content = user_content

    async def handler_func(self):
        reply_content = await agent_main(self.user_id, self.user_content)
        send_message(self.user_id, reply_content)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.handler_func())
        finally:
            loop.close()

# 获取access_token
def acquire_access_token():
    appid = os.environ.get('WECHAT_APPID')
    secret = os.environ.get('WECHAT_APPSECRET')
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    response = requests.get(token_url)
    return response.json()["access_token"]

# 主动给用户发送消息
def send_message(user_id, message_content):
    access_token = acquire_access_token()

    # 构造客服消息发送请求
    request_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    data = {
        "touser": user_id,
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }
    # print(data)
    response = requests.post(request_url, data=bytes(json.dumps(data, ensure_ascii=False), encoding="utf-8"))
    # print(response.json())


