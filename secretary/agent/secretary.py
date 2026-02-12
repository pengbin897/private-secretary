import os, logging, json
from datetime import datetime
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.memory import InMemoryMemory
from agentscope.formatter import OpenAIChatFormatter
from agentscope.tool import Toolkit, ToolResponse

from secretary.models import UserSchedule, CharacterTracks


logger = logging.getLogger(__name__)

RECORDER_PROMPT = f"""
你是一个私人助理，你的主要工作是协助用户进行日程管理。
当前时间为:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}。
当你需要添加一条待办日程的时候，请先查询一下是否已有相同的待办（触发时间、内容、紧急程度相同），如果有，不要重复添加
"""
FEATURE_ANALYZER_PROMPT = f"""

"""
memory = InMemoryMemory()

def load_history_messages(user_id: int) -> list:
    """
    加载用户的历史消息
    """
    try:
        character_tracks = CharacterTracks.objects.get(owner_id=user_id)
    except CharacterTracks.DoesNotExist:
        return []
    if not character_tracks.history_messages:
        return []
    return json.loads(character_tracks.history_messages)

def save_history_messages(user_id: int, history_messages: list):
    """
    保存用户的历史消息
    """
    # 获取或创建对象
    obj, created = CharacterTracks.objects.get_or_create(
        owner_id=user_id,
        defaults={'history_messages': '[]'}  # 初始为空列表的 JSON 字符串
    )

    # 解析现有消息
    if created:
        messages = []
    else:
        try:
            messages = json.loads(obj.history_messages)
        except (TypeError, json.JSONDecodeError):
            messages = []  # 容错：如果字段不是合法 JSON，重置为空列表

    messages.extend(history_messages)
    # 保存回数据库
    obj.history_messages = json.dumps(messages, ensure_ascii=False)
    obj.save()

async def agent_main(user_id: int, user_message: str, reply_hook: callable):
    def add_schedule(content: str, urgency_grade: int, fire_time: datetime) -> ToolResponse:
        """
        添加一条待办日程
        Args:
            content(str): {待办/日程事项的详细内容}
            urgency_grade(int): {紧急程度，1:低，2:中，3:高}
            fire_time(datetime): {事项设定的触发时间}
        """
        UserSchedule.objects.create(
            owner_id=user_id,
            content=content,
            urgency_grade=urgency_grade,
            fire_time=fire_time
        )
        print(f"给用户ID[{user_id}]添加一条日程信息：{content}，触发时间：{fire_time}")
        return ToolResponse(
            content=f"已添加一条日程信息：{content}，触发时间：{fire_time}"
        )

    def get_schedule_list() -> ToolResponse:
        """
        查询用户所有日程列表
        """
        schedules = UserSchedule.objects.filter(owner_id=user_id).order_by('-fire_time')
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                'id': schedule.id,
                'content': schedule.content,
                'fire_time': schedule.fire_time,
            })
        return ToolResponse(
            content=json.dumps(schedule_list)
        )

    llm = OpenAIChatModel(
        model_name=os.environ.get("OPENAI_MODEL_NAME"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        client_kwargs={"base_url": os.environ.get("OPENAI_BASE_URL")},
        stream=True,
    )
    toolkit = Toolkit()
    toolkit.register_tool_function(add_schedule)
    toolkit.register_tool_function(get_schedule_list)

    # 先通过记忆库对用户进行特征分析及更新
    feature_analyzer = ReActAgent(
        name="feature_analyzer",
        model=llm,
        sys_prompt=FEATURE_ANALYZER_PROMPT,
        formatter=OpenAIChatFormatter(),
        memory=memory,
    )

    # 再根据特征分析结果进行后续的对话
    recorder = ReActAgent(
        name="recorder",
        model=llm,
        sys_prompt=RECORDER_PROMPT,
        formatter=OpenAIChatFormatter(),
        memory=memory,
        toolkit=toolkit
    )
    msg = Msg(name=user_id, role="user", content=user_message)
    reply = await recorder(msg)
    reply_hook(reply.get_text_content())

