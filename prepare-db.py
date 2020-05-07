#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

from app.models.user import Roles, UserModel
from app.models.exam import *
from app.models.analysis import *
from run_app import app
import datetime
import numpy as np


if __name__ == '__main__':
    print(QuestionModel.objects(id='5eb286adc38fabcba71f8ccf').first().text)
    # print(type(admin.role))
    # print(admin.role)
    # print(admin.role == Roles.Default)
    # print(admin.role == Roles.Admin)
    #
    # user1 = UserModel()
    # user1.email = 'aaa@site.com'
    # user1.password = app.md5_hash('1234')
    # user1.name = '张三'
    # user1.role = Roles.Default
    # # user1.student_id = 'Mf1832144'
    # user1.save()
    #
    # user2 = UserModel()
    # user2.email = 'bbb@site.com'
    # user2.password = app.md5_hash('1234')
    # user2.name = '李四'
    # user2.role = Roles.Default
    # # user2.student_id = 'Mf1832110'
    # user2.save()
    # questions = QuestionModel.objects(q_type=2)
    # for question in questions:
    #     analysis_list = AnalysisModel.objects(question_num=question['q_id'])
    #     key_hit = question['weights']['key_hit_times']
    #     detail_hit = question['weights']['detail_hit_times']
    #     for a in analysis_list:
    #         for i in range(len(key_hit)):
    #             key_hit[i] += a['key_hits'][i]
    #         temp_d = []
    #         for d in a['detail_hits']:
    #             temp_d += d
    #         for i in range(len(detail_hit)):
    #             detail_hit[i] += temp_d[i]
    #     print(key_hit)
    #     print(detail_hit)
    #     question['weights']['key_hit_times'] = key_hit
    #     question['weights']['detail_hit_times'] = detail_hit
    #     question.save()
    # questions = QuestionModel.objects(q_id=3)
    # for question in questions:
    #     question['in_optimize'] = False
    #     question['last_optimize_time'] = None
    #     if question['q_type'] != 2:
    #         question.save()
    #         continue
    #     key_words = question['wordbase']['keywords']
    #     detail_words = []
    #     for lst in question['wordbase']['detailwords']:
    #         detail_words += lst
    #
    #     key_weight = list(map(lambda x: 100 / (len(key_words) + 1), key_words + [1]))
    #     key_hits = list(map(lambda x: 0.0, key_words))
    #     detail_weight = list(map(lambda x: 100 / (len(detail_words) + 1), detail_words + [1]))
    #     detail_hits = list(map(lambda x: 0.0, detail_words))
    #     question['weights']['key'] = key_weight
    #     question['weights']['detail'] = detail_weight
    #     question.save()
    # currents = CurrentTestModel.objects()
    # for current in currents:
    #     for question in current['questions'].values():
    #         if question['q_type'] != 2:
    #             question['analysed'] = True
    #     current.save()

