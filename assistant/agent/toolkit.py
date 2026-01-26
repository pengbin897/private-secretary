from datetime import datetime
from agentscope.tool import Toolkit, ToolResponse

from superadmin.models import UserSchedule


def add_schedule(content: str, fire_time: datetime) -> ToolResponse:
    """
    添加日程
    Args:
        content(str): {待办/日程事项的详细内容}
        fire_time(datetime): {事项设定的触发时间}
    """
    # UserSchedule.objects.create(
    #     content=content,
    #     fire_time=fire_time
    # )
    print(f"添加一条日程信息：{content}，触发时间：{fire_time}")
    return ToolResponse(
        content=f"已添加一条日程信息：{content}，触发时间：{fire_time}"
    )


def delete_schedule() -> ToolResponse:
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


toolkit = Toolkit()
toolkit.register_tool_function(add_schedule)
# toolkit.register_tool_function(delete_schedule)
# toolkit.register_tool_function(get_schedule_list)
# toolkit.register_tool_function(get_schedule_detail)
