from app.models.analysis import AnalysisModel
from app.models.exam import HistoryTestModel
from app.exam.exam_config import ExamConfig

import expression.new_analysis as analysis_util


class Analysis(object):

    def re_analysis(self, analysis_question):
        """对指定题目重新分析
        :param analysis_question: 要被分析的 question
        """
        print("analysis out", analysis_question['q_id'])
        total_key, total_detail, count = 0, 0, 0
        # 首先，将analysis表里所有这道题的答案都重新分析一遍
        old_analysis_list = AnalysisModel.objects(question_num=analysis_question['q_id'])
        for analysis in old_analysis_list:
            self.compute_score_and_save(analysis, analysis['voice_features'], analysis_question,
                                        analysis['test_start_time'])
            total_key = analysis['score_key']
            total_detail = analysis['score_detail']
            count += 1

        # 然后，将current中未被分析的部分分析一遍
        histories = HistoryTestModel.objects(all_analysed=False)
        print(len(histories))
        for test in histories:
            questions = test['questions']
            all_analysed = True
            for question in questions.values():
                if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished' and \
                        not question['analysed']:
                    analysis = self.compute_score_and_save(test, analysis_question['q_id'], analysis_question,
                                                           test['test_start_time'])
                    if analysis is None:
                        continue
                    question['analysed'] = True
                    total_key = analysis['score_key']
                    total_detail = analysis['score_detail']
                    count += 1
                all_analysed = all_analysed and question['analysed']
            test['all_analysed'] = all_analysed
            test.save()

        # 更新难度
        if count != 0:
            mean = (total_key * ExamConfig.key_percent + total_detail * ExamConfig.detail_percent) / count
            difficulty = mean / ExamConfig.full_score
            analysis_question['level'] = round(10 - difficulty * 10)
            analysis_question.save()
        pass

    @staticmethod
    def init_analysis():
        """根据 current.questions 中的第二类问题初始化 analysis 表
        """
        # for question in QuestionModel.objects(q_type=2).order_by('q_id'):
        #     init_process(question)
        pass

    @staticmethod
    def init_process(analysis_question):
        """对指定问题进行 analysis 表的初始化工作

        :param analysis_question: 要被分析的 question
        """
        # 然后，将current中未被分析的部分分析一遍
        print('-----------------------')
        print('start to analyse question ', analysis_question['q_id'])
        histories = HistoryTestModel.objects()
        print(len(histories))
        for test in histories:
            questions = test['questions']
            all_analysed = True
            for question in questions.values():
                if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished':
                    Analysis.compute_score_and_save(test, analysis_question['q_id'], analysis_question,
                                                    test['test_start_time'])
                    question['analysed'] = True
                all_analysed = all_analysed and question['analysed']
            test['all_analysed'] = all_analysed
            test.save()
        pass

    @staticmethod
    def compute_score_and_save(test, q_id, question, test_start_time):
        print("analysis inner:compute_score_and_save:q_id: %s, test_start_time: %s"
              % (q_id, test['test_start_time']))
        try:
            analysis = AnalysisModel()
            analysis['exam_id'] = test['id'].__str__()
            analysis['user'] = test['user_id']
            analysis['question_id'] = question['q_id'].__str__()
            analysis['question_num'] = q_id
            features = question['feature']
            voice_features = {
                'rcg_text': features['rcg_text'],
                'last_time': features['last_time'],
                'interval_num': features['interval_num'],
                'interval_ratio': features['interval_ratio'],
                'volumes': features['volumes'],
                'speeds': features['speeds'],
            }
            analysis['voice_features'] = voice_features
            print('test_start_time: ' + test['test_start_time'].__str__())
            feature_result = analysis_util.analysis_features(None, question['wordbase'], voice_features=voice_features)
            score = analysis_util.compute_score(feature_result['key_hits'], feature_result['detail_hits'],
                                                question['weights']['key'], question['weights']['detail'])
            analysis['score_key'] = float(score['key'])
            analysis['score_detail'] = float(score['detail'])
            analysis['key_hits'] = feature_result['key_hits']
            analysis['detail_hits'] = feature_result['detail_hits']
            analysis['test_start_time'] = test_start_time
            analysis.save()
            return analysis
        except Exception as e:
            print('################')
            print('ERROR:compute_score_and_save: test.id: %s, q_id: %s -->' % (test.id, q_id))
            print(e)


# if __name__ == '__main__':
#     import sys
#     print(sys.path)
#     print(analysis_util)
#     analysis = Analysis()
#     analysis.init_analysis()
