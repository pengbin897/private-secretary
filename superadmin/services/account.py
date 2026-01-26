
from django.contrib.auth.models import User
from superadmin.models import UserManageAccount

def register_user(
        username: str,
        channel: str,
        token: str,
        password: str='123456',
        openid: str=None,
        unionid: str=None,
        nickname: str=None,
        headimgurl: str=None,
        credential: str=None) -> User:
    ''' 用户首次注册 '''
    user = User.objects.create_user(username=username, password=password)
    account = UserManageAccount.objects.create(
        pk=user.pk,
        wx_openid=openid,
        wx_unionid=unionid,
        user_id=user.pk,
        token=token,
        channel=channel,
        nickname=nickname,
        headimgurl=headimgurl,
        credential=credential,
        balance=50) # 新注册用户赠送50个点

    return account

