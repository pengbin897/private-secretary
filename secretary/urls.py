from django.urls import path

from .views import *

urlpatterns = [
    path("wxamp_request", WxampRequestView.as_view()),
    path("wxamp_notify/<str:user_id>", WxampNotifyUserView.as_view()),
    path("submit_menus", submit_menus),
    
    # 日程管理接口
    path("schedules", UserScheduleListView.as_view(), name="schedule_list"),
    path("schedules/<int:schedule_id>", UserScheduleDetailView.as_view(), name="schedule_detail"),
    path("schedules/<int:schedule_id>/delete", UserScheduleDeleteView.as_view(), name="schedule_delete"),

    path("messages", UserMessagesView.as_view(), name="messages"),
]
