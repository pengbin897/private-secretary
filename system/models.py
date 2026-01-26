from django.db import models


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
