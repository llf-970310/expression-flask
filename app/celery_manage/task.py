import os
import sys
from app.models.exam import *
from app.models.analysis import *
from app import scheduler

dir_name = '/Users/cuihua/Documents/workspace/mooctest/Expression/exp-docker/'
# dir_name = '/home/ise/docker/exp-docker/'
# dir_name = '/Users/gyue/Programs/exp-docker/'
sys.path.append(dir_name)
sys.path.append(os.path.join(dir_name, 'expression'))
sys.path.append(os.path.join(dir_name, 'model_test'))

import expression.new_analysis as analysis_util


def test_db():
    print('test_db')
    for question in QuestionModel.objects(q_type=2).order_by('q_id'):
        print(question['q_id'])
    pass


def collect_current_to_analysis():
    """将 current 表中新出现的已评分分析的题目搬运到 analysis
    """
    print('collect_current_to_analysis')
    for question in QuestionModel.objects(q_type=2).order_by('q_id'):
        collect(question)
    pass


def collect(analysis_question):
    """对指定问题进行 analysis 表的初始化工作

    :param analysis_question: 要被分析的 question
    """
    # 然后，将current中未被分析的部分分析一遍
    print('-----------------------')
    print('start to analyse question ', analysis_question['q_id'])
    currents = CurrentTestModel.objects(all_analysed=False)
    print(len(currents))
    for test in currents:
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
                total_key = analysis['score_key']
                total_detail = analysis['score_detail']
            all_analysed = all_analysed and question['analysed']
        test['all_analysed'] = all_analysed
        test.save()
    pass


def __compute_score_and_save(analysis, voice_features, question, test_start_time):
    feature_result = analysis_util.analysis_features(None, question['wordbase'], voice_features=voice_features)
    score = analysis_util.compute_score(feature_result['key_hits'], feature_result['detail_hits'],
                                        question['weights']['key'], question['weights']['detail'])
    analysis['score_key'] = score['key']
    analysis['score_detail'] = score['detail']
    analysis['key_hits'] = feature_result['key_hits']
    analysis['detail_hits'] = feature_result['detail_hits']
    analysis['test_start_time'] = test_start_time
    print(score)
    analysis.save()
    print('saved: ' + analysis['question_num'].__str__() + '        ' + analysis['user'].__str__() + '        ' +
          analysis['test_start_time'].__str__())
    pass
