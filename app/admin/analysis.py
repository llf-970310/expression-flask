# import os
# import sys
# from app.models.exam import *
# from app.models.analysis import *
# from app.exam.config import ExamConfig
#
# dir_name = '/Users/gyue/Programs/exp-docker/'
# # dir_name = '/home/ise/docker/exp-docker/'
# sys.path.append(dir_name)
# sys.path.append(os.path.join(dir_name, 'expression'))
# sys.path.append(os.path.join(dir_name, 'model_test'))
#
# import expression.new_analysis as analysis_util


def re_analysis(analysis_question):
    # print("analysis out", analysis_question['q_id'])
    # total_key, total_detail, count = 0, 0, 0
    # # 首先，将analysis表里所有这道题的答案都重新分析一遍
    # old_analysis_list = AnalysisModel.objects(question_num=analysis_question['q_id'])
    # for analysis in old_analysis_list:
    #     compute_score_and_save(analysis, analysis['voice_features'], analysis_question)
    #     total_key = analysis['score_key']
    #     total_detail = analysis['score_detail']
    #     count += 1
    #
    # # 然后，将current中未被分析的部分分析一遍
    # currents = CurrentTestModel.objects(all_analysed=False)
    # print(len(currents))
    # for test in currents:
    #     questions = test['questions']
    #     all_analysed = True
    #     for question in questions.values():
    #         if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished' and \
    #                 not question['analysed']:
    #             print("analysis inner", analysis_question['q_id'])
    #             analysis = AnalysisModel()
    #             analysis['exam_id'] = test['id'].__str__()
    #             analysis['user'] = test['user_id']
    #             analysis['question_id'] = question['q_id'].__str__()
    #             analysis['question_num'] = analysis_question['q_id']
    #             voice_features = {
    #                 'rcg_text': question['feature']['rcg_text'],
    #                 'last_time': question['feature']['last_time'],
    #                 'interval_num': question['feature']['interval_num'],
    #                 'interval_ratio': question['feature']['interval_ratio'],
    #                 'volumes': question['feature']['volumes'],
    #                 'speeds': question['feature']['speeds'],
    #             }
    #             analysis['voice_features'] = voice_features
    #             compute_score_and_save(analysis, voice_features, analysis_question)
    #             question['analysed'] = True
    #             total_key = analysis['score_key']
    #             total_detail = analysis['score_detail']
    #             count += 1
    #         all_analysed = all_analysed and question['analysed']
    #     test['all_analysed'] = all_analysed
    #     test.save()
    #
    # # 更新难度
    # mean = (total_key * ExamConfig.key_percent + total_detail * ExamConfig.detail_percent) / count
    # difficulty = mean / ExamConfig.full_score
    # analysis_question['level'] = round(10 - difficulty * 10)
    # analysis_question.save()
    pass


def compute_score_and_save(analysis, voice_features, question):
    # feature_result = analysis_util.analysis_features(None, question['wordbase'], voice_features=voice_features)
    # score = analysis_util.compute_score(feature_result['key_hits'], feature_result['detail_hits'],
    #                                     question['weights']['key'], question['weights']['detail'])
    # analysis['score_key'] = score['key']
    # analysis['score_detail'] = score['detail']
    # analysis['key_hits'] = feature_result['key_hits']
    # analysis['detail_hits'] = feature_result['detail_hits']
    # print(score)
    # analysis.save()
    pass


# if __name__ == '__main__':
#     print(sys.path)
#     print(analysis_util)
