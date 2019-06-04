import abc

from flask import current_app, jsonify

from app import errors
from app.admin.admin_config import ScoreConfig
from app.exam.exam_config import ExamConfig
from app.models.analysis import *
from app.models.user import UserModel
from . import admin, util
from .algorithm import OptimizeAlgorithm


@admin.route('/score/question', methods=['GET'])
def get_score_of_all_questions():
    """获取各题目平均分的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_questions')

    all_answers = AnalysisModel.objects().order_by('question_num')
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = QuestionNumMapper()
    result = __generate_result_from_dict(mapper.map_answers(all_answers), 'questionId')
    return jsonify(errors.success({'result': result}))


@admin.route('/score/question/<id>', methods=['GET'])
def get_score_of_specific_questions(id):
    """获取某题目的成绩情况 TODO

    :param id: 题号ID
    :return: 该问题的成绩情况
    """
    current_app.logger.info('get_score_of_specific_questions   ' + id)

    all_answers = AnalysisModel.objects(question_num=id).order_by('date')
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = DateMapper()
    result = __generate_result_from_dict(mapper.map_answers(all_answers), 'date')
    return jsonify(errors.success({'result': result}))


@admin.route('/score/user', methods=['GET'])
def get_score_of_all_users():
    """获取各用户平均分的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_users')

    all_answers = AnalysisModel.objects()
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = UserMapper()
    result = __generate_result_from_dict(mapper.map_answers(all_answers), 'userEmail')

    # map_answers_by_user() 返回的结果中 key 为 ObjectId，需要改为 email
    for item in result:
        cur_user_id = item['userEmail']
        cur_user = UserModel.objects(id=cur_user_id).first()
        cur_user_email = cur_user if cur_user else ScoreConfig.DEFAULT_USER_EMAIL + cur_user_id.__str__()
        item['userEmail'] = cur_user_email
    return jsonify(errors.success({'result': result}))


@admin.route('/score/user/<user_email>', methods=['GET'])
def get_score_of_specific_users(user_email):
    """获取某用户的成绩情况

    :param user_email: 用户邮箱
    :return: 该用户的成绩情况
    """
    current_app.logger.info('get_score_of_specific_users   ' + user_email)

    cur_user = UserModel.objects(email=user_email).first()
    if not cur_user:
        return jsonify(errors.User_not_exist)

    all_answers = AnalysisModel.objects(user=cur_user['id']).order_by('date')
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = DateMapper()
    result = __generate_result_from_dict(mapper.map_answers(all_answers), 'date')
    return jsonify(errors.success({'result': result}))


class AbstractMapper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def map_answers(self, answers):
        """
        将回答 list 按照一定规则对应为 dict
        """
        return


class QuestionNumMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照题号对应

        :param answers: 所有的回答
        :return: key 为题号，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_question_id = answer['question_num']
            if cur_question_id in res:
                res[cur_question_id].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_question_id] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


class UserMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照用户对应

        :param answers: 所有的回答
        :return: key 为用户 ObjectId，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_user = answer['user']
            if cur_user in res:
                res[cur_user].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_user] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


class DateMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照回答日期对应

            :param answers: 所有的回答
            :return: key 为日期，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_date = util.convert_date_to_str(answer['test_start_time'])
            if cur_date in res:
                res[cur_date].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_date] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


def __generate_result_from_dict(dict, result_key_name):
    """

    :param dict: {result_key: {key, detail}]}
    :param result_key_name: 结果集中的 key 值
    :return:
    """
    algorithm = OptimizeAlgorithm()

    result = []
    for key in dict:
        cur_answers = dict[key]
        detail_scores = [cur_answer['detail'] for cur_answer in cur_answers]
        key_scores = [cur_answer['key'] for cur_answer in cur_answers]

        key_score = algorithm.analysis_score(key_scores, ExamConfig.full_score)['mean']
        detail_score = algorithm.analysis_score(detail_scores, ExamConfig.full_score)['mean']
        result.append({
            result_key_name: key,
            'mainScore': format(key_score, ScoreConfig.DEFAULT_NUM_FORMAT),
            'detailScore': format(detail_score, ScoreConfig.DEFAULT_NUM_FORMAT),
            'totalScore': format(key_score * ExamConfig.key_percent + detail_score * ExamConfig.detail_percent,
                                 ScoreConfig.DEFAULT_NUM_FORMAT)
        })
    return result
