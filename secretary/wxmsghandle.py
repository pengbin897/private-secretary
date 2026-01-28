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


class WxMsgHandle:
    # 获取access_token
    def acquire_access_token(self):
        appid = os.environ.get('WECHAT_APPID')
        secret = os.environ.get('WECHAT_APPSECRET')
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
        response = requests.get(token_url)
        return response.json()["access_token"]

    # 主动给用户发送消息
    def send_message(self, user_id, message_content):
        access_token = self.acquire_access_token()

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

    def handle_user_content(self, user_id, user_content):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(chat(user_id, user_content))
            finally:
                loop.close()
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def send_message(self, user_id, message_content):
        access_token = self.acquire_access_token()
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