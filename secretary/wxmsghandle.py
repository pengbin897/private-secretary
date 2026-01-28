import threading, asyncio
import os, json, requests
from .agent.main import chat


class MessageHandle:
    def __init__(self):
        self.loop = None
        self.thread = None

    def start(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def submit_coro(self, coro):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.loop)
        else:
            raise RuntimeError("Background loop not running")


class WxMsgHandle(threading.Thread):
    def __init__(self, user_id, user_content):
        super().__init__()
        self.daemon = True
        self.user_id = user_id
        self.user_content = user_content

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handle_user_content(self.user_id, self.user_content))
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

async def handle_user_content(user_id, user_content):
    reply_content = await chat(user_id, user_content)
    send_message(user_id, reply_content)

