import requests


""" 阿里云百炼的API """
api_key = "sk-90cb7ca9e5de40dd813756824f0d5fab"


# 上传待训练的图片文件
def add_training_files(file_paths, descriptions):
    url = "https://dashscope.aliyuncs.com/api/v1/files"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    files = []
    for file_path in file_paths:
        files.append(('files', open(file_path, 'rb')))
    
    data = {
        'descriptions': descriptions
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()['data']['upload_files']
    else:
        response.raise_for_status()


# 创建人像训练任务
def create_figure_task(original_image_ids):
    url = "https://dashscope.aliyuncs.com/api/v1/fine-tunes"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": 'facechain-finetune',
        "training_file_ids": original_image_ids
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


# 获取训练任务状态
def get_finetune_task_status(task_id):
    url = f"https://dashscope.aliyuncs.com/api/v1/fine-tunes/{task_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['status'] == 'SUCCEEDED':
        return True
    else:
        response.raise_for_status()


# 获取异步任务结果
def get_task_result(task_id):
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['status'] == 'SUCCEEDED':
        return response.json()['output']['image_url']
    else:
        response.raise_for_status()
    

# 生成个性人物的API（同时兼容使用训练模型和免训练直接生成）
def generate_figure(source_image_url, template_image_urls = None, style = None):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/album/gen_potrait"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    data = {
        "model": "facechain-generation",
        "input": {
            "template_url": template_image_urls,
            "user_urls": source_image_url  # 免训练时需要
        },
        "parameters": {
            "style": style,
            "n": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['task_id']:
        return response.json()['output']['task_id']
    else:
        response.raise_for_status()


# 创建模特试衣的任务
def create_dressing_task(params):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    data = {
        "model": "aitryon-plus",
        "input": {
            "person_image_url": params['image'],
            "top_garment_url": params['prompt'],
            "bottom_garment_url": params['prompt'],
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['task_id']:
        return response.json()['output']['task_id']
    else:
        response.raise_for_status()


# 创建生成鞋靴模特图的任务
def create_shoemodel_task(params):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/virtualmodel/generation"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    data = {
        "model": "shoemodel-v1",
        "parameters": {
            "n": 1
        },
        "input": {
            "template_image_url": params['image'],
            "shoe_image_url": params['prompt'],
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['task_id']:
        return response.json()['output']['task_id']
    else:
        response.raise_for_status()


# 创建艺术字任务
def create_wordart_task(params):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/wordart/texture"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"
    }
    data = {
        "model": "wordart-texture",
        "parameters": {
            "n": 1
        },
        "input": {
            "text": {
                "text_content": params['text'],
                "ttf_url": params['ttf_url'],
                "font_name": "fangzhengkaiti"
            },
            "texture_style": "waterfall",
            "prompt": params['prompt'],
            "ref_image_url": params['ref_image_url']
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200 and response.json()['output'] and response.json()['output']['task_id']:
        return response.json()['output']['task_id']
    else:
        response.raise_for_status()


