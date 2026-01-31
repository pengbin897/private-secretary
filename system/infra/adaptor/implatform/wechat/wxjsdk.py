''' 微信公众号授权网页之后使用JSDK相关的后台 API '''
import os, requests
import logging


logger = logging.getLogger(__name__)

appid = os.environ.get('WECHAT_APPID')
appsecret = os.environ.get('WECHAT_APPSECRET')

def oauth_access_token(code: str) -> dict:
    """
    获取access_token
    :return:
    """
    url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={appsecret}&code={code}&grant_type=authorization_code'
    res = requests.get(url)
    errcode = res.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin access token failed, code: {code}, errcode: {errcode}, errmsg: {res.json().get("errmsg")}')
        return None
    return res.json()

def verify_access_token(access_token: str, openid: str) -> bool:
    """
    验证access_token
    :param access_token:
    :param openid:
    :return:
    """
    url = f'https://api.weixin.qq.com/sns/auth?access_token={access_token}&openid={openid}'
    res = requests.get(url)
    errcode = res.json().get('errcode')
    if errcode:
        logger.warning(f'verify weixin token failed, token: {access_token}, errcode: {errcode}, errmsg: {res.json().get("errmsg")}')
        return False
    return True

def refresh_access_token(refresh_token: str) -> dict:
    """
    刷新access_token
    :param appid:
    :param appsecret:
    :param refresh_token:
    :return:
    """
    url = f'https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={appid}&grant_type=refresh_token&refresh_token={refresh_token}'
    res = requests.get(url)
    errcode = res.json().get('errcode')
    if errcode:
        logger.warning(f'refresh weixin access token failed, token: {refresh_token}, errcode: {errcode}, errmsg: {res.json().get("errmsg")}')
        return None
    return res.json()

def get_user_info(access_token: str, openid: str) -> dict:
    """
    获取用户信息
    :param access_token:
    :param openid:
    :return:
    """
    url = f'https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN'
    res = requests.get(url)
    errcode = res.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin user info failed, token: {access_token}, errcode: {errcode}, errmsg: {res.json().get("errmsg")}')
        return None
    # 将res以UTF-8编码解码后再转成json格式
    res.encoding = 'utf-8'
    return res.json()

''' 获取微信JSAPI的ticket '''
def get_jsapi_ticket(access_token):
    url = f'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin jsapi ticket failed, token: {access_token}, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('ticket')

