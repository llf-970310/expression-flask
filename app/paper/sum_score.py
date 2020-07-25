#!/usr/bin/env python3
# coding: utf-8
from app.exam.exam_config import ReportConfig

q_dimensions = {
    1: ['quality'],
    2: ['key', 'detail'],
    3: ['structure', 'logic'],
    4: [],
    5: ['key', 'detail'],
    6: ['key', 'detail']
}


def compute_exam_score(scores, paper_type: list):
    # todo 这里暂时改成能用
    """
    计算考试成绩
    :param scores: 考试各题成绩数组
    :param paper_type: 试题类型列表 [q_type, q_type, ...]
    :return: 考试个维度成绩和总成绩
    """
    print(scores)
    # for i in range(ExamConfig.total_question_num, 0, -1):
    #     if not score.get(i):
    #         print("in not")
    #         print(score.get(i))
    #         score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
    # print(score)

    # total_quality = 0
    # total_key = 0
    # total_detail = 0
    # total_structure = 0
    # total_logic = 0
    # for k, v in scores.items():
    #     total_quality += v.get('quality', 0)
    #     total_key += v.get('key', 0)
    #     total_detail += v.get('detail', 0)
    #     total_structure += v.get('structure', 0)
    #     total_logic += v.get('logic', 0)
    #
    # x = {
    #     'quality': round(total_quality, 6),  # 1个题算平均?
    #     'key': round(total_key * 0.25, 6),  # 4个题算平均?
    #     'detail': round(total_detail * 0.25, 6),  # 4个题算平均?
    #     'structure': round(total_structure, 6),  # 1个题算平均?
    #     'logic': round(total_logic, 6)  # 1个题算平均?
    # }
    # x['total'] = round(x["quality"] * 0.3 + x["key"] * 0.35 + x["detail"] * 0.15 + x["structure"] * 0.1 + x[
    #     "logic"] * 0.1, 6)
    # data = {"音质": x['quality'], "结构": x['structure'], "逻辑": x['logic'],
    #         "细节": x['detail'], "主旨": x['key'], "total": x['total']}

    tmp_total = {'quality': 0, 'key': 0, 'detail': 0, 'structure': 0, 'logic': 0}
    cnt_total = {'quality': 0, 'key': 0, 'detail': 0, 'structure': 0, 'logic': 0}  # 求平均分时的除数
    avg_total = {}  # 平均分
    for i, q_type in enumerate(paper_type):
        dimensions = q_dimensions.get(q_type)
        q_score = scores[i + 1]
        for dim in dimensions:
            tmp_total[dim] += q_score.get(dim, 0)
            cnt_total[dim] += 1
    for dim in tmp_total:
        if cnt_total[dim]:
            avg_total[dim] = tmp_total[dim] / cnt_total[dim]
        else:
            avg_total[dim] = 0
    total = round(avg_total["quality"] * 0.3 + avg_total["key"] * 0.35 + avg_total["detail"] * 0.15 +
                  avg_total["structure"] * 0.1 + avg_total["logic"] * 0.1, 6)
    data = {"音质": avg_total['quality'], "结构": avg_total['structure'], "逻辑": avg_total['logic'],
            "细节": avg_total['detail'], "主旨": avg_total['key'], "total": total}
    print(data)
    return data
