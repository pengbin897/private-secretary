import os, logging
from datetime import datetime
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.memory import InMemoryMemory
from agentscope.formatter import OpenAIChatFormatter
from agentscope.tool import Toolkit, ToolResponse


logger = logging.getLogger(__name__)

SYS_PROMPT = f"""
你是一个私人助理，你的主要工作是协助用户进行日程管理。
当前时间为:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}。
"""
memory = InMemoryMemory()

async def agent_main(user_id: str, user_message: str, reply_hook: callable):
    def add_schedule(content: str, fire_time: datetime) -> ToolResponse:
        """
        添加一条待办日程
        Args:
            content(str): {待办/日程事项的详细内容}
            fire_time(datetime): {事项设定的触发时间}
        """
        # UserSchedule.objects.create(
        #     content=content,
        #     fire_time=fire_time
        # )
        print(f"给用户[{user_id}]添加一条日程信息：{content}，触发时间：{fire_time}")
        return ToolResponse(
            content=f"已添加一条日程信息：{content}，触发时间：{fire_time}"
        )

    def delete_schedule() -> ToolResponse:
        """
        删除一条日程待办
        Args:
            content(str): {待办/日程事项的详细内容}
            fire_time(datetime): {事项设定的触发时间}
        """
        return ToolResponse(
            content=""
        )

    def get_schedule_list() -> ToolResponse:
        return ToolResponse(
            content=""
        )

    def get_schedule_detail() -> ToolResponse:
        return ToolResponse(
            content=""
        )
    
    llm = OpenAIChatModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        client_kwargs={"base_url": os.environ.get("OPENAI_BASE_URL")},
        stream=True,
    )
    toolkit = Toolkit()
    toolkit.register_tool_function(add_schedule)
    # toolkit.register_tool_function(delete_schedule)
    # toolkit.register_tool_function(get_schedule_list)
    # toolkit.register_tool_function(get_schedule_detail)

    agent = ReActAgent(
        name="secretary",
        model=llm,
        sys_prompt=SYS_PROMPT,
        formatter=OpenAIChatFormatter(),
        memory=memory,
        toolkit=toolkit
    )
    msg = Msg(name=user_id, role="user", content=user_message)
    reply = await agent(msg)
    reply_hook(reply.get_text_content())
