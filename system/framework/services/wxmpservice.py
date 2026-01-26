import requests
import logging

from system.framework.services import wechatpayservice

logger = logging.getLogger(__name__)

appid = 'wxc8a3082c12838873'
appsecret = 'df1b38a4dd0ec1b1f360e6f557876836'

# 根据微信小程序的code获取小程序用户openid和unionid
def get_user_state(code: str) -> dict:
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={appsecret}&js_code={code}&grant_type=client_credential'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warn(f'get weixin miniprogram user info failed, code: {code}, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json()

def acquire_access_token():
    ''' 获取小程序调用凭证 '''
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warn(f'get weixin access token failed, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('access_token')

def create_pay_order(order_desc, order_no, amount, payer):
    ''' 创建支付订单 '''
    return wechatpayservice.create_pay_order(appid, order_desc, order_no, amount, payer)
