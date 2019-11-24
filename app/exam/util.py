# coding: utf-8

import time
from .exam_config import ExamConfig


def compute_exam_score(score):
    """
    计算考试成绩
    :param score: 考试各题成绩数组
    :return: 考试个维度成绩和总成绩
    """
    print(score)
    for i in range(ExamConfig.total_question_num, 0, -1):
        if not score.get(i):
            print("in not")
            print(score.get(i))
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
    print(score)
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
    print(data)
    return data


def get_server_date_str(separator='') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    return time.strftime("%%Y%s%%m%s%%d" % (separator, separator), time.localtime(time.time()))


if __name__ == '__main__':
    pass
    # x = {
    #     "name": "褚东宇"
    # }
    # path = save_dict_to_path(x, name='1234.json', dir='/Users/tangdaye/ttt/ttt/')
    # dic = get_dict_from_path(path)
