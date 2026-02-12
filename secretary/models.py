from django.db import models

from system.common.mixin import TenantModelMixin


class UserSchedule(TenantModelMixin):
    class UrgencyGrade(models.IntegerChoices):
        LOW = 1, '低'
        MEDIUM = 2, '中'
        HIGH = 3, '高'

    class Status(models.IntegerChoices):
        PENDING = 0, '待办'
        COMPLETED = 1, '已完成'
        CANCELLED = 2, '已取消'

    record_time = models.DateTimeField(verbose_name='记录时间', auto_now_add=True)
    urgency_grade = models.IntegerField(verbose_name='紧急程度', choices=UrgencyGrade.choices, default=UrgencyGrade.LOW)
    content = models.TextField(verbose_name='待办/日程事项的详细内容')
    categories = models.CharField(verbose_name='分类标签,用逗号分隔', max_length=128)
    fire_time = models.DateTimeField(verbose_name='触发时间')
    status = models.IntegerField(verbose_name='状态', choices=Status.choices, default=Status.PENDING)


class CharacterTracks(TenantModelMixin):
    history_messages = models.TextField(verbose_name='历史消息')
    character_summary = models.TextField(verbose_name='对用户特征的详细总结')

    class Meta:
        verbose_name = '基于对话历史记录形成的对用户特征、记忆点的描述'
        verbose_name_plural = '用户特征的形成轨迹'

