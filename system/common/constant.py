from django.db import models

# digishow使用
class ProductType(models.IntegerChoices):
    CARTOON_SHOW = 1
    DRESSING_ON = 2
    WORD_ART = 3

class ToolType(models.IntegerChoices):
    CVDREAMOVING = 1
    AIPOSTER = 2
    WORDART = 3
    PHOTORECOVER = 4

class UserChannel(models.IntegerChoices):
    TRANDITIONAL = 1  # 传统账号密码
    SMS = 2  # 短信验证码
    WECHAT_MINI_PROGRAM = 3  # 微信小程序
    WECHAT_H5 = 4  # 微信H5

