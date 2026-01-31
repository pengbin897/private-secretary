import threading, asyncio
from .agent.main import agent_main
from system.infra.adaptor.implatform.wechat.wxamp import send_message_to_user


def handle_wxmessage_async(user_id, user_content):
    def reply_hook(reply_content):
        send_message_to_user(user_id, reply_content)
        
    def handle_wxmessage():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(agent_main(user_id, user_content, reply_hook))
        finally:
            loop.close()

    threading.Thread(target=handle_wxmessage).start()


