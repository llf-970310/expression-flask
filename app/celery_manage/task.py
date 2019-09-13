import os
import sys
from app.models.exam import *
from app.models.analysis import *
from app.exam.exam_config import ExamConfig
from app.exam.util import *
from app import scheduler

dir_name = '/Users/cuihua/Documents/workspace/mooctest/Expression/exp-docker/'
# dir_name = '/home/ise/docker/exp-docker/'
# dir_name = '/Users/gyue/Programs/exp-docker/'
sys.path.append(dir_name)
sys.path.append(os.path.join(dir_name, 'expression'))
sys.path.append(os.path.join(dir_name, 'model_test'))

import expression.new_analysis as analysis_util


def move_current_to_history():
    """
    将 current 表中超时且未在处理中的部分搬运到history
    """
    print('move_current_to_history')
    for current in CurrentTestModel.objects({}):
        test_start_time = current['test_start_time']
        now_time = datetime.datetime.utcnow()
        delta_seconds = (now_time - test_start_time).total_seconds()
        if delta_seconds >= ExamConfig.exam_total_time and question_not_handling(current['questions']):
            print("remove %s" % current.id.__str__())
            history = HistoryTestModel()
            history['current_id'] = current.id.__str__()
            history['user_id'] = current['user_id']
            history['test_start_time'] = current['test_start_time']
            history['paper_type'] = current['paper_type']
            history['current_q_num'] = current['current_q_num']
            history['score_info'] = current['score_info']
            history['questions'] = current['questions']
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
            current.delete()


def question_not_handling(question_dict):
    for value in question_dict.values():
        if value['status'] == 'handling':
            return False
    return True


def collect_history_to_analysis():
    """将 current 表中新出现的已评分分析的题目搬运到 analysis
    """
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
                print("analysis inner", analysis_question['q_id'], test['test_start_time'])
                analysis = AnalysisModel()
                analysis['exam_id'] = test['id'].__str__()
                analysis['user'] = test['user_id']
                analysis['question_id'] = question['q_id'].__str__()
                analysis['question_num'] = analysis_question['q_id']
                voice_features = {
                    'rcg_text': question['feature']['rcg_text'],
                    'last_time': question['feature']['last_time'],
                    'interval_num': question['feature']['interval_num'],
                    'interval_ratio': question['feature']['interval_ratio'],
                    'volumes': question['feature']['volumes'],
                    'speeds': question['feature']['speeds'],
                }
                analysis['voice_features'] = voice_features
                print('test_start_time: ' + test['test_start_time'].__str__())
                __compute_score_and_save(analysis, voice_features, analysis_question, test['test_start_time'])
                question['analysed'] = True
            all_analysed = all_analysed and question['analysed']
        test['all_analysed'] = all_analysed
        test.save()
    pass


def __compute_score_and_save(analysis, voice_features, question, test_start_time):
    feature_result = analysis_util.analysis_features(None, question['wordbase'], voice_features=voice_features)
    score = analysis_util.compute_score(feature_result['key_hits'], feature_result['detail_hits'],
                                        question['weights']['key'], question['weights']['detail'])
    analysis['score_key'] = float(score['key'])
    analysis['score_detail'] = float(score['detail'])
    analysis['key_hits'] = feature_result['key_hits']
    analysis['detail_hits'] = feature_result['detail_hits']
    analysis['test_start_time'] = test_start_time
    analysis.save()
    print('saved: ' + analysis['question_num'].__str__() + '        ' + analysis['user'].__str__() + '        ' +
          analysis['test_start_time'].__str__())
    pass


# if __name__ == '__main__':
#     from mongoengine import connect
#
#     MONGODB = {
#         'NAME': 'expression_flask',
#         'HOST': '47.98.174.59',
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
