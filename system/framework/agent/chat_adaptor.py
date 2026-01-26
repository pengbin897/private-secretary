
from openai import OpenAI

from common.exceptions import ApiException


aliyun_api_key = 'sk-ecd3a8775842431b969fb139e1d6f4e0'

def chat(prompt: str) -> str:
    client = OpenAI(
        api_key=aliyun_api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    try:
        completion = client.chat.completions.create(
            model="deepseek-v3.1",
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        response_content = completion.choices[0].message.content
    except Exception as e:
        raise ApiException(str(e))
    return response_content

