import json
import requests

from common.exceptions import ApiException


yuanbao_api_key = 'aF6jpBr39QjL1nv8bhLoZcun1Myxfyq7'

def chat(prompt: str) -> str:
    try:
        response = requests.post(
            'https://yuanqi.tencent.com/openapi/v1/agent/chat/completions',
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {yuanbao_api_key}"
            },
            data=json.dumps({
                "assistant_id": '1980142276194759424',
                "user_id": 'pengbin119',
                "stream": False,
                "messages": [{
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": prompt
                    }]
                }]
            })
        )
    except Exception as e:
        raise ApiException(str(e))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise ApiException(response.json()['error']['message'])
