import requests
import json
import os
import random
import string
import logging

from system.models import SystemSettings

logger = logging.getLogger(__name__)


""" modelscope上的facechain API https://modelscope.cn/studios/CVstudio/FaceChain-FACT """

def get_token():
    '''获取modelscope web端的访问token'''
    return SystemSettings.objects.get(key='MS_TOKEN').value

def generate_sid():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    return random_string


def fetch_gradioapi_result(url: str, headers: dict):
    with requests.Session() as session:
        response = session.get(url, headers=headers, stream=True)
        # 检查响应状态码
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=2048):
                # 处理每个块
                if chunk:
                    str = chunk.decode('utf-8')[6:]
                    print(str)
                    data = json.loads(str)
                    if data['msg'] == 'process_completed':
                        if data['success']:
                            return data['output']['data'][0][0]['image']['path']
                        else:
                            return False
                else:
                    break
        else:
            logger.error(f"fetch task response error code: {response.status_code}, error message: {response.content}")
            return False

def facechain_generate(ori_img_path: str, lora_style_name: str):
    payload = {
        "data": [
            "",
            "风格广场风格(Modelscope hub styles)",
            "074, arm_tattoo, body_writing, breasts, earrings, jewelry, shoulder_tattoo, tattoo, tree, upper_body, raw photo, masterpiece, solo, medium shot, high detail face, photorealistic, best quality",
            "(nsfw:2), paintings, sketches, (worst quality:2), (low quality:2), lowers, normal quality, ((monochrome)), ((grayscale)), logo, word, character, bad hand, tattoo, (username, watermark, signature, time signature, timestamp, artist name, copyright name, copyright),low res, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans, extra fingers, fewer fingers, strange fingers, bad hand, mole, ((extra legs)), ((extra hands))",
            [{
                "image": {
                    "path": ori_img_path,
                    "url": f"https://cvstudio-facechain-fact.ms.show/file={ori_img_path}",
                    "orig_name": os.path.basename(ori_img_path),
                    "size": 38831,
                    "mime_type": "image/jpeg",
                    "meta": {
                        "_type": "gradio.FileData"
                    }
                },
                "caption": None
            }],
            1,
            lora_style_name,
            "preset",
            0.8,
            None,
            "是(Yes)",
            512,
            512
        ],
        "event_data": None,
        "fn_index": 12,
        "trigger_id": 48,
        "dataType": [
            "textbox",
            "radio",
            "textbox",
            "textbox",
            "gallery",
            "number",
            "textbox",
            "dropdown",
            "slider",
            "image",
            "radio",
            "slider",
            "slider"
        ],
        "session_hash": generate_sid()
    }



