from django.db import models

from common.mixin import TenantModelMixin


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


