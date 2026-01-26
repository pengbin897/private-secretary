from typing import List

from django.http import JsonResponse
from rest_framework import status


def k_to_camel(name):
    words = name.split('_')
    # 保持第一个单词小写，其余单词首字母大写
    return words[0] + ''.join(word.capitalize() for word in words[1:])

def dict_to_camel(d):
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            new_key = k_to_camel(key)
            if isinstance(value, dict):
                result[new_key] = dict_to_camel(value)
            else:
                result[new_key] = value
        return result
    elif isinstance(d, list):
        return [dict_to_camel(item) for item in d]
    else:
        return d
    

class Page(dict):
    """
    分页对象
    """
    def __init__(self, total: int, records: List, current_page: int = 1, page_size: int = 10, **kwargs):
        super().__init__(**{'total': total, 'results': dict_to_camel(records), 'current': current_page, 'size': page_size})


class Result(JsonResponse):
    """
     接口统一返回对象
    """
    def __init__(self, code, message="success", data=None, response_status=status.HTTP_200_OK, **kwargs):
        response_data = {"errcode": code, "errmsg": message, 'data': dict_to_camel(data)}
        super().__init__(data=response_data, status=response_status, **kwargs)


def success(data=None, **kwargs):
    """
    获取一个成功的响应对象
    :param data: 接口响应数据
    :return: 请求响应对象
    """
    return Result(code = 0, data=data, **kwargs)

def error(message):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message)

def page_success(data, total: int, current_page: int = 1, page_size: int = 10, **kwargs):
    '''
    返回一个成功的分页结果
    '''
    return success(Page(total, records=data, current_page=current_page, page_size=page_size), **kwargs)
