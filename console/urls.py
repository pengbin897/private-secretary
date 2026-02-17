from django.urls import path

from . import views


urlpatterns = [
    path('user/manage/list', views.UserListQueryView.as_view()),
    path('user/manage/details', views.UserDetailsView.as_view()),
    path('user/manage/details/<int:user_id>', views.UserDetailsView.as_view()),

    path('sys/menu/list', views.MenuListQueryView.as_view()),
    path('sys/menu', views.SysMenuSettingView.as_view()),
    path('sys/menu/<int:menu_id>', views.SysMenuSettingView.as_view()),
    path('sys/datamodel/list', views.SysDataModelListView.as_view()),
    path('sys/datamodel', views.SysDataModelView.as_view()),

    path('9type/questions', views.QuestionConfigView.as_view()),
    path('9type/report/list', views.UserReportListView.as_view()),
    path('9type/report/<int:report_id>', views.UserReportView.as_view()),
]

