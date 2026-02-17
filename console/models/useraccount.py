from django.db import models
from django.contrib.auth.models import User



# 管理端的数据模型，不需要租户属性
class Privilege(models.Model):
    ''' 功能权限的定义基础表 '''
    class Value(models.IntegerChoices):
        ADMIN = 1, '管理员'
        cvdreamoving = 2, '追影的权限'

    privilege = models.IntegerField(verbose_name='权限', null=True)
    description = models.CharField(verbose_name='描述', max_length=128, null=True)

    class Meta:
        db_table = 'system_privilege'
        verbose_name = '功能权限的定义基础表'
        verbose_name_plural = verbose_name



class UserAccessLog(models.Model):
    ''' 用户访问日志 '''
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    access_time = models.DateTimeField(verbose_name='访问时间', auto_now_add=True)
    ip = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.CharField(verbose_name='用户代理', max_length=128, null=True)

    class Meta:
        db_table = 'system_user_access_log'
        verbose_name = '用户访问日志'
        verbose_name_plural = verbose_name


class UserFeedback(models.Model):
    ''' 用户反馈 '''
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    feedback_time = models.DateTimeField(verbose_name='反馈时间', auto_now_add=True)
    feedback_content = models.TextField(verbose_name='反馈内容')
    
    class Meta:
        db_table = 'system_user_feedback'
        verbose_name = '用户反馈'
        verbose_name_plural = verbose_name
    

