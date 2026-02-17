from django.db import models
from django.contrib.auth.models import User

from system.common.mixin import TenantModelMixin


class UserOrder(TenantModelMixin):
    ''' 用户第三方支付的订单 '''
    class Status(models.IntegerChoices):
        FOR_PAID = 0, '等待支付'
        PAID = 1, '已支付'
        CANCELED = 2, '已取消'

    order_no = models.CharField(verbose_name='订单号，系统内创建的', max_length=128, unique=True)
    trade_no = models.CharField(verbose_name='交易号，第三方支付返回的', max_length=128, null=True)
    provider = models.CharField(verbose_name='支付渠道方', max_length=128, default='weixin')
    order_desc = models.CharField(verbose_name='订单描述', max_length=256, null=True)
    amount = models.IntegerField(verbose_name='订单金额，单位分', null=True)
    payer = models.CharField(verbose_name='付款人信息', max_length=128, null=True)
    status = models.IntegerField(verbose_name='订单状态', choices=Status.choices, default=Status.FOR_PAID)

    class Meta:
        db_table = 'system_user_order'
        verbose_name = '用户订单'
        verbose_name_plural = verbose_name


class UserTradeRecord(TenantModelMixin):
    ''' 用户交易明细 '''
    class TYPE(models.IntegerChoices):
        CHARGE = 1, '充值'
        CONSUME = 2, '消费'

    order_no = models.CharField(verbose_name='订单号，系统内创建的，有的交易有，有的没有', max_length=128, null=True)
    trade_type = models.IntegerField(verbose_name='交易类型', choices=TYPE.choices, default=1)
    amount = models.IntegerField(verbose_name='交易积分', default=0)
    trade_time = models.DateTimeField(verbose_name='交易发生时间', auto_now_add=True)
    remark = models.CharField(verbose_name='备注说明', max_length=256, null=True)
    
    class Meta:
        db_table = 'system_user_trade_record'
        ordering = ['-trade_time']
        verbose_name = '交易明细'
        verbose_name_plural = verbose_name

