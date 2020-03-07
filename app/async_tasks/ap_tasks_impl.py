#!/usr/bin/env python3
# coding: utf-8

from __future__ import absolute_import
import datetime

from app.async_tasks.utils import get_a_redis_lock
from app.models.exam import CurrentStatisticsModel, CurrentTestModel, HistoryTestModel, QuestionModel
from app.admin.analysis import Analysis
from app.exam.exam_config import ExamConfig
from app.exam.util import compute_exam_score


def func_example():
    if not get_a_redis_lock(func_example, 24 * 3 * 3600):
        print('cannot get a redis lock, exit now')
        return
    print('this is an example apscheduler task')
    # raise Exception('nothing wrong, just wanna except')


def move_current_to_history():
    """
    1. 删除 current 表中 user_id 为空 或为 'batchtest' 的记录
    2. 将 current 表中超时且未在处理中的部分搬运到history
    """
    if not get_a_redis_lock(move_current_to_history):
        return
    print('move_current_to_history')
    stat = CurrentStatisticsModel()
    stat.total_cnt = CurrentTestModel.objects().count()
    bt_tests = CurrentTestModel.objects(__raw__={
        '$or': [{'user_id': 'null'}, {'user_id': ''}, {'user_id': 'batchtest'}]
    })
    stat.batch_test_cnt = bt_tests.count()
    bt_tests.delete()
    stat.user_test_cnt = CurrentTestModel.objects().count()
    stat.save()
    for document in CurrentTestModel.objects:
        test_start_time = document['test_start_time']
        now_time = datetime.datetime.utcnow()
        delta_seconds = (now_time - test_start_time).total_seconds()
        if delta_seconds >= ExamConfig.exam_total_time and question_process_finished(document['questions']):
            print("remove %s" % str(document.id))
            history = HistoryTestModel()
            history['current_id'] = str(document.id)
            history['user_id'] = document['user_id']
            openid = document.get('openid')
            if openid:
                history['openid'] = openid
            history['test_start_time'] = document['test_start_time']
            history['paper_type'] = document['paper_type']
            history['current_q_num'] = document['current_q_num']
            history['score_info'] = document['score_info']
            history['questions'] = {}
            for i, q in document['questions'].items():
                _type = q.get('type')
                if _type in [1, 2, 3, '1', '2', '3']:
                    history.update({i: q})
            history['all_analysed'] = False
            # 防止history中的总分还有未计算的
            if not history['score_info']:
                print("compute score in celery task...")
                questions = history['questions']
                score = {}
                for i in range(ExamConfig.total_question_num, 0, -1):
                    if questions[str(i)]['status'] == 'finished':
                        score[i] = questions[str(i)]['score']
                    else:
                        score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
                print("compute score...")
                print(score)
                history['score_info'] = compute_exam_score(score)
                history.save()
                print(history['score_info'])
            history.save()
            document.delete()


def question_process_finished(question_dict):
    for value in question_dict.values():
        _type = value.get('type')
        if _type in [1, 2, 3, '1', '2', '3']:
            if value.get('status') == 'finished':
                return True
    return False


def collect_history_to_analysis():
    """将 current 表中新出现的已评分分析的题目搬运到 analysis
    """
    if not get_a_redis_lock(collect_history_to_analysis):
        return
    print('collect_history_to_analysis')
    history_list = HistoryTestModel.objects()

    for question in QuestionModel.objects(q_type=2).order_by('q_id'):
        collect(question, history_list)
    pass


def collect(analysis_question, history_list):
    """对指定问题进行 analysis 表的初始化工作

    :param analysis_question: 要被分析的 question
    :param history_list: 测试历史
    """
    # 然后，将history中未被分析的部分分析一遍
    print('-----------------------')
    print('start to analyse question ', analysis_question['q_id'])
    print(len(history_list))
    for test in history_list:
        questions = test['questions']
        all_analysed = True
        for question in questions.values():
            if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished' and \
                    not question['analysed']:
                analysis = Analysis.compute_score_and_save(test, analysis_question['q_id'], analysis_question,
                                                           test['test_start_time'])
                if analysis is None:
                    continue
                print('saved: ' + str(analysis['question_num']) + '        ' + str(analysis['user']) + '        ' +
                      str(analysis.test_start_time))
                question['analysed'] = True
            all_analysed = all_analysed and question['analysed']
        test['all_analysed'] = all_analysed
        test.save()

# if __name__ == '__main__':
#     from mongoengine import connect
#
#     MONGODB = {
#         'NAME': 'expression_flask',
#         'HOST': 'mongo-server.expression.hosts',
#         'PORT': 27017,  # caution: integer here (unlike django default)
#         'NEED_AUTH': True,
#         'AUTH_MECHANISM': 'SCRAM-SHA-1',
#         'USER': 'iselab',
#         'PASSWORD': 'iselab###nju.cn'
#     }
#     connect(MONGODB['NAME'], host=MONGODB['HOST'], port=MONGODB['PORT'],
#             username=MONGODB['USER'], password=MONGODB['PASSWORD'], authentication_source=MONGODB['NAME'],
#             authentication_mechanism=MONGODB['AUTH_MECHANISM'])
#     print(sys.path)
#     print(analysis_util)
#     questions = QuestionModel.objects(q_type=2).order_by('q_id')
#     print(len(questions))
#     for question in questions:
#         print(question["q_id"])
#         collect(question)
