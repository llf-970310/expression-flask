

import time
import os
import json
from .exam_config import ApiConfig, ExamConfig


def compute_exam_score(score):
    """
    计算考试成绩
    :param score: 考试各题成绩数组
    :return: 考试个维度成绩和总成绩
    """
    for i in range(ExamConfig.total_question_num, 0, -1):
        if not score.get(i):
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
    x = {
        "quality": round(score[1]['quality'], 6),
        "key": round(score[2]['key'] * 0.25 + score[3]['key'] * 0.25 + score[4]['key'] * 0.25 + score[5][
            'key'] * 0.25, 6),
        "detail": round(score[2]['detail'] * 0.25 + score[3]['detail'] * 0.25 + score[4]['detail'] * 0.25 +
                        score[5]['detail'] * 0.25, 6),
        "structure": round(score[6]['structure'], 6),
        "logic": round(score[6]['logic'], 6)
    }
    x['total'] = round(x["quality"] * 0.3 + x["key"] * 0.35 + x["detail"] * 0.15 + x["structure"] * 0.1 + x[
        "logic"] * 0.1, 6)
    data = {"音质": x['quality'], "结构": x['structure'], "逻辑": x['logic'],
            "细节": x['detail'], "主旨": x['key'], "total": x['total']}
    return data


def get_date_str(separator='') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    return time.strftime("%%Y%s%%m%s%%d" % (separator, separator), time.localtime(time.time()))


"""
Desc:   以指定文件名，保存dict到指定文件夹，若文件夹不存在则自动创建，若指定路径下已有同名文件自动备份原文件（添加覆盖标记和覆盖时间戳）
Input:  dict，文件名，路径
Output: path
"""


def save_dict_to_path(dic, name, dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    path = os.path.join(dir, name)
    if os.path.exists(path):
        os.rename(path, os.path.join(dir, ApiConfig.backup_prefix + str(int(time.time())) + name))
    with open(path, 'w') as f:
        f.write(json.dumps(dic, ensure_ascii=False))
    return path


"""
Desc:   从指定文件路径中获得dict，如果路径不存在返回None
Input:  路径
Output: dict
"""


def get_dict_from_path(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        dic = json.loads(f.read())
    return dic


"""
Desc:   按照文本获得文件内容,如果路径不存在返回None
Input:  路径
Output: 文件内容
"""


def get_content_from_path(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        content = f.read()
    return content


"""
Desc:   以指定名称保存二进制文件到指定目录
Input:  文件，目录，名称
Output: 路径
"""


def save_file_to_path(file, name, dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    path = os.path.join(dir, name)
    if os.path.exists(path):
        os.rename(path, os.path.join(dir, ApiConfig.backup_prefix + str(int(time.time())) + name))
    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path


if __name__ == '__main__':
    pass
    # x = {
    #     "name": "褚东宇"
    # }
    # path = save_dict_to_path(x, name='1234.json', dir='/Users/tangdaye/ttt/ttt/')
    # dic = get_dict_from_path(path)
