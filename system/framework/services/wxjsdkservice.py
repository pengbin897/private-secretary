import requests
import logging

logger = logging.getLogger(__name__)


def get_jsapi_ticket(access_token):
    url = f'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi'
    response = requests.get(url)
    errcode = response.json().get('errcode')
    if errcode:
        logger.warn(f'get weixin jsapi ticket failed, token: {access_token}, errcode: {errcode}, errmsg: {response.json().get("errmsg")}')
        return None
    return response.json().get('ticket')



