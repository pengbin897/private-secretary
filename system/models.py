from django.db import models
from django.contrib.auth.models import User

from system.common.constant import UserChannel


class DataModelDict(models.Model):
    ''' 数据字典 '''
    type = models.CharField(verbose_name='字典大类', max_length=64, null=True)
    name = models.CharField(verbose_name='字典大类的名字', max_length=64, null=True)
    key = models.CharField(verbose_name='字典属性的索引键', max_length=64, unique=True, null=True)
    value = models.CharField(verbose_name='字典属性的值', max_length=64, null=True)
    label = models.CharField(verbose_name='字典属性的显示名称', max_length=64, null=True)

    class Meta:
        db_table = 'system_datamodel_dict'
        verbose_name = '数据字典'
        verbose_name_plural = verbose_name


class SysMenuSettings(models.Model):
    ''' 系统菜单设置 '''
    name = models.CharField(verbose_name='名字', max_length=64)
    path = models.CharField(verbose_name='前端路径', max_length=64)
    parent = models.ForeignKey('self', verbose_name='父级', on_delete=models.CASCADE, null=True)
    component = models.CharField(verbose_name='组件路径', max_length=64, null=True)
    permission = models.CharField(verbose_name='可访问权限', max_length=64, null=True)
    icon = models.CharField(verbose_name='图标', max_length=16, null=True)
    title = models.CharField(verbose_name='显示标题', max_length=64)
    isHide = models.BooleanField(verbose_name='是否隐藏', default=False)
    isKeepAlive = models.BooleanField(verbose_name='是否缓存', default=True)
    isAffix = models.BooleanField(verbose_name='是否固定', default=False)
    isFull = models.BooleanField(verbose_name='是否全屏', default=False)

    class Meta:
        db_table = 'system_menu_settings'
        verbose_name = '系统菜单设置'
        verbose_name_plural = verbose_name


class SystemSettings(models.Model):
    ''' 系统设置 '''
    key = models.CharField(verbose_name='设置项的键', max_length=64, unique=True)
    value = models.CharField(verbose_name='设置项的值', max_length=64, null=True)
    description = models.TextField(verbose_name='设置项的描述', null=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name = '系统设置'
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
