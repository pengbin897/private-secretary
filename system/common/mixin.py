
from django.db import models
from django.forms.models import model_to_dict

from system.models import UserManageAccount


class TenantModelMixin(models.Model):
    ''' 租户相关的模型 '''
    owner =  models.ForeignKey(UserManageAccount, models.CASCADE, verbose_name='所属用户', null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)

    def to_dict(self):
        data = model_to_dict(self)
        data['create_time'] = self.create_time
        data['update_time'] = self.update_time
        data['owner'] = self.owner.user.username
        return data

    class Meta:
        abstract = True
        ordering = ['-create_time']
