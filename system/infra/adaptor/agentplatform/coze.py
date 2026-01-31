
import os
import time
from cozepy import COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageType

coze_api_token = os.environ.get('COZE_API_TOKEN')
bot_id = os.environ.get('COZE_BOT_ID')
user_id = 'pengbin119'

def chat(query: str) -> str:
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text(query),
        ],
    )
    for message in chat_poll.messages:
        # print(message)
        if message.type == MessageType.ANSWER:
            return message.content

