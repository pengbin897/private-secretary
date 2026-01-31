from django.db import models
from django.contrib.auth.models import User

from system.infra.common.constant import UserChannel


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


class UserManageAccount(models.Model):
    ''' 管理用户的账户 '''
    user = models.OneToOneField(User, verbose_name='用户', on_delete=models.CASCADE)
    token = models.CharField(verbose_name='验证用的token', max_length=256, null=True)
    wx_openid = models.CharField(verbose_name='微信openid', max_length=128, null=True)
    wx_unionid = models.CharField(verbose_name='微信unionid', max_length=128, null=True)
    nickname = models.CharField(verbose_name='微信的昵称', max_length=128, null=True)
    headimgurl = models.CharField(verbose_name='微信头像', max_length=256, null=True)
    phone = models.CharField(verbose_name='手机号', max_length=12, null=True)
    channel = models.IntegerField(verbose_name='用户渠道', choices=UserChannel.choices, default=UserChannel.TRANDITIONAL.value)
    credential = models.TextField(verbose_name='用户凭证相关的原始数据，json格式存储', null=True)
    infomation = models.TextField(verbose_name='用户不重要的基本资料都放里面（性别、省市等），json格式存储', null=True)
    balance = models.IntegerField(verbose_name='积分余额', default=0)
    level = models.IntegerField(verbose_name='用户等级', default=1)
    register_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True, null=True)
    last_login_time = models.DateTimeField(verbose_name='最后登录时间', auto_now_add=True, null=True)

    class Meta:
        db_table = 'system_user_manage_account'
        verbose_name = '管理用户账户'


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
    

