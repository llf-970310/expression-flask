#!/usr/bin/env python3
# coding: utf-8

from __future__ import absolute_import
import datetime

from app.async_tasks.utils import mutex_with_redis
from app.models.exam import CurrentTestModel, HistoryTestModel
from app.models.current_stat import CurrentStatisticsModel
from app.models.question import QuestionModel
from app.admin.analysis import Analysis
from app.paper import compute_exam_score


@mutex_with_redis(3600 * 6)
def func_example():
    print('[Example][APSTask]this is an example apscheduler task', datetime.datetime.now())
    # raise Exception('nothing wrong, just wanna except')


@mutex_with_redis(600)
def user_based_cf():
    print('[Example][APSTask][user_based_cf]', datetime.datetime.now())
    from app.paper.utils.collaborative_filter import CollaborativeFilter
    cf = CollaborativeFilter()
    cf.create_reverse_table()
    cf.create_weight_matrix()
    cf.calc_similarity_matrix()
    # cf.save_similar_users()


@mutex_with_redis(600)
def move_current_to_history():
    """
    1. 删除 current 表中 user_id 为空 或为 'batchtest' 的记录
    2. 将 current 表中超时且未在处理中的部分搬运到history
    """
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
        if document.paper_tpl_id not in ['5eb84af7aaaae82807e5312a', '5eb84af7aaaae82807e5312b']:  # TODO 解决硬编码
            continue
        # test_start_time = document['test_start_time']
        now_time = datetime.datetime.utcnow()
        # delta_seconds = (now_time - test_start_time).total_seconds()
        if now_time >= document.test_expire_time and question_process_finished(document['questions']):
            print("remove %s" % str(document.id))
            history = HistoryTestModel()
            history['current_id'] = str(document.id)
            history['user_id'] = document['user_id']
            openid = document['openid']
            if openid:
                history['openid'] = openid
            history['test_start_time'] = document['test_start_time']
            history['test_expire_time'] = document['test_expire_time']
            history['paper_type'] = document['paper_type']
            history['paper_tpl_id'] = document['paper_tpl_id']
            history['current_q_num'] = document['current_q_num']
            history['score_info'] = document['score_info']
            history['questions'] = document['questions']
            # for i, q in document['questions'].items():
            #     _type = q.q_type
            #     if _type in [1, 2, 3, '1', '2', '3']:
            #         history['questions'][i] = q
            history['all_analysed'] = False
            # 防止history中的总分还有未计算的
            if not history['score_info']:
                print("compute score in celery task...")
                questions = history['questions']
                score = {}
                for i in range(len(document.questions), 0, -1):
                    if questions[str(i)]['status'] == 'finished':
                        score[i] = questions[str(i)]['score']
                    else:
                        score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
                print("compute score...")
                print(score)
                history['score_info'] = compute_exam_score(score, history.paper_type)
                history.save()
                print(history['score_info'])
            history.save()
            document.delete()


def question_process_finished(question_dict):
    for value in question_dict.values():
        if value['status'] != 'finished' and value['status'] != 'error':
            return False
    return True


@mutex_with_redis(600)
def collect_history_to_analysis():
    """将 current 表中新出现的已评分分析的题目搬运到 analysis
    """
    print('collect_history_to_analysis')
    history_list = HistoryTestModel.objects()

    for question in QuestionModel.objects(q_type=2).order_by('index'):
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
#     questions = QuestionModel.objects(q_type=2).order_by('index')
#     print(len(questions))
#     for question in questions:
#         print(question["q_id"])
#         collect(question)
