from datetime import datetime
import binascii
import os
import base64
import json
import requests
import logging

logger = logging.getLogger(__name__)

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


mchid = '1648330305'
cert_no = '3DB532B7500308FF368C3A676C0857A4E359E6AB'  # 证书编号
private_key_pem = '''-----BEGIN RSA PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtTJWX8Omb8dF+
bgG1b/6Zd2/+PNUOh+LTFo5fASIpWsgUWp7w1dzFWLgit3ohTekgKZLDMZknlixM
wbTbDz3CkdSwutcHKFd1frZVLmVYhrLUj51LBZw6DpF9rcLnUx1ncw+LaRFFZ7JR
GkfgQ1/rJDL4ff1zyidYNp1lpy0CxXAnW5PaymN57q0vvaCBpBMKYCqkJsKZZxhG
2tFzxC5gDYbqpKsAFrsUPRdOIop/kxFMiPIPvuvcNgRwT58rR/rhmmQFPKyMxHFA
axQz1JssblRhlef+5D1nNyOwD9YoMAiWfbeRqOuFMMkHgcMKdhX19HypaB7LS1Q7
YYOebqURAgMBAAECggEAT425mm9wfjMLLZPIWwcXhFHM6pP4ZlxA5xASuVAm438W
HCnhjsNOPpXUqbM6cHF4lFghVFO/b+nDWlUN9gXQHzKcxahvr4x4YaqSfxX2ViY3
j9aBqX/g0NIBPgV3VIPWGrg6KZBI6miI9iwvVKb5MFOExofnwrDJUPh5VsHgqsVA
oxGB/mcu98/cWKczaW6JoUTEY2gPCNNtIS9j9U3PbrinxOph7e0rvfesT1PxfIbt
pGJfZbihLW4Jt7UoJZx6nwI2aBevF9baR8Q/4ztchZxjv1uS9k7X/swC5Sp3KM0b
bBBPg4Mdl0Yit758yXy642Ry3ywoEfj5TyIT1UAzQQKBgQDXF8NW5+9nY0qA7lY+
mbWKZwaAsVODCoNxxOu0nsRlBGHMrWOy5Z5n5IGEv7r27OsVs561rezbA9niSnN1
at2YryNtSqQmxGcfdPBqlcOSJpVZ44+IWYYQtfMBiNbPEChdqMZY9pIIUUzuyCHg
mg9DfLsLjszZ9vAthByvb82IqQKBgQDOQgK2pfkardw0a4Lmlb3aGTmjWAnh2waf
q2DHEfYSPlsU1zONKlSSbzDjBPyrC7r7gnNUb9fyUEUht1FYSDNPVidfnGmtf9C6
phOcPKJBeSglL2n4qxiidpHIXvJUj0Abgz4d4K5Vc+YU/wsGqb2sMIKcQebhOC1p
aQgiATTyKQKBgQCHxs5eW8a6QulS/iCfH7SDi4mFT2riO47CEIah298pzVxXMdTP
pzcZahuASu+g0+mKJ3q2QPZVQtcVi93abv03VsdMRGPevPhD2TOydJuh9I0u0wFW
Fv0UK2ccvt6qkw6IIPQkUHHaokeoK9mGyHl+JoyEPT5/EOyILu9Up4TdEQKBgDSr
5sV93P9TJsi8K9F2q+TmTDHKabujky1zNmOf0pcWFWxdCG0kQjSi8HkI7P1BIZ7Y
0VretObMWNsjVUKWLYQ1HBjueI419be0cY2UblsJ9ZaJZSZ7iu7yGIhytq+hZV2h
Rlua5OotjrQN7WLmNemi+betnKgnEHG6wLjuVfcBAoGBAKvLYFLjYZhePoSCKrZA
vuF8Ebtb5zxURywSfr3nTEO0OMP4w75XbV8sHb+8gnbNc4e9HxtRjZal94g9mfG2
gsNUn37wXZhR7aM4eeQsbzaCYDl/uQpPE2rZIZ1HXGaMDBEC1eNz6RzkWQGjDoW+
CmrXGNgBPAyqmH1QnIb0HwZt
-----END RSA PRIVATE KEY-----'''


# 生成微信支付的v3签名
def sign_wepay_v3_api(http_method, url, body):
    """
    生成微信支付V3接口要求的签名值
    
    :param http_method: HTTP请求方法，例如 'POST'
    :param url: 请求的URL路径（不带域名）
    :param nonce_str: 请求随机串
    :param body: 请求体（字符串格式，若为空则传空字符串）
    :param private_key_pem: 商户私钥内容（PEM格式字符串）
    :return: Base64编码的签名值
    """
    timestamp = str(int(datetime.now().timestamp()))
    nonce_str = binascii.hexlify(os.urandom(16)).upper().decode('utf-8')
    # 构建签名串
    signature_str = (
        f"{http_method}\n"
        f"{url}\n"
        f"{timestamp}\n"
        f"{nonce_str}\n"
        f"{body}\n"
    )
    # 计算SHA256哈希
    hash_obj = SHA256.new(signature_str.encode('utf-8'))
    # 加载商户私钥
    private_key = RSA.import_key(private_key_pem)
    # 使用 PKCS#1 v1.5 进行签名
    signer = pkcs1_15.new(private_key)
    raw_signature = signer.sign(hash_obj)
    # Base64 编码
    signature = base64.b64encode(raw_signature).decode('utf-8')
    return timestamp, nonce_str, signature

def sign_wepay_jsapi(appid, prepay_id):
    ''' 生成微信支付的jsapi签名 '''
    timestamp = str(int(datetime.now().timestamp()))
    nonce_str = binascii.hexlify(os.urandom(16)).upper().decode('utf-8')
    signature_str = (
        f"{appid}\n"
        f"{timestamp}\n"
        f"{nonce_str}\n"
        f"prepay_id={prepay_id}\n"
    )
    # 计算SHA256哈希
    hash_obj = SHA256.new(signature_str.encode('utf-8'))
    # 加载商户私钥
    private_key = RSA.import_key(private_key_pem)
    # 使用 PKCS#1 v1.5 进行签名
    signer = pkcs1_15.new(private_key)
    raw_signature = signer.sign(hash_obj)
    # Base64 编码
    signature = base64.b64encode(raw_signature).decode('utf-8')
    return timestamp, nonce_str, signature


def create_pay_order(appid, order_desc, order_no, amount, payer):
    ''' 创建支付订单 '''
    url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    body = {
        'appid': appid,
        'mchid': mchid,
        'description': order_desc,
        'out_trade_no': order_no,
        'amount': {
            'total': amount,
            'currency': 'CNY'
        },
        'payer': {
            'openid': payer
        },
        'notify_url': 'https://tools.linkgeeks.com.cn/api/wxpay/notify'
    }
    body_str = json.dumps(body)
    timestamp, nonce_str, signature = sign_wepay_v3_api('POST', '/v3/pay/transactions/jsapi', body_str)
    auth_info = f'WECHATPAY2-SHA256-RSA2048 mchid="{mchid}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{cert_no}"'
    header['Authorization'] = auth_info
    response = requests.post(url, headers=header, data=body_str)
    if response.status_code != 200:
        logger.error(f'预创建订单失败,errcode: {response.json().get("errcode")}, errmsg: {response.json().get("errmsg")}')
        return None
    # print(response.json())
    # 生成jsapi签名
    timestamp, nonce_str, signature = sign_wepay_jsapi(appid, response.json().get('prepay_id'))
    return {
        'prepayId': response.json().get('prepay_id'),
        'timestamp': timestamp,
        'nonceStr': nonce_str,
        'signature': signature,
    }

