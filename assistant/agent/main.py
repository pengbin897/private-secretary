import logging, asyncio
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.memory import InMemoryMemory
from agentscope.formatter import OpenAIChatFormatter

from .toolkit import toolkit


logger = logging.getLogger(__name__)

llm = OpenAIChatModel(
    model_name="qwen-plus-2025-07-28",
    api_key="sk-ecd3a8775842431b969fb139e1d6f4e0",
    client_kwargs={"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    stream=True,
)


agent = ReActAgent(
    name="assistant",
    model=llm,
    sys_prompt="你是一个助手，请根据用户的问题给出回答。",
    formatter=OpenAIChatFormatter,
    memory=InMemoryMemory(),
    toolkit=toolkit
)


async def chat(user_id, user_message):
    msg = Msg(name=user_id, role="user", content=user_message)
    reply = await agent(msg)
    return reply.get_text_content()


if __name__ == "__main__":
    asyncio.run(chat("1234567890", "你好"))
    