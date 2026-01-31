''' 小程序后台 API '''
import os, requests, logging


logger = logging.getLogger(__name__)

appid = os.environ.get('WX_MINIPROGRAM_APPID')
appsecret = os.environ.get('WX_MINIPROGRAM_APPSECRET')

# 根据微信小程序的code获取小程序用户openid和unionid
def get_user_state(code: str) -> dict:
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={appsecret}&js_code={code}&grant_type=client_credential'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin miniprogram user info failed, code: {code}, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json()

def acquire_access_token():
    ''' 获取小程序调用凭证 '''
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'get weixin access token failed, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('access_token')

def verify_access_token(access_token, openid):
    url = f'https://api.weixin.qq.com/sns/auth?access_token={access_token}&openid={openid}'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warning(f'verify weixin access token failed, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('access_token')
