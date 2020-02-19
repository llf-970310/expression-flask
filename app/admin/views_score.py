import abc

from flask import current_app, jsonify

from app import errors
from app.admin.admin_config import ScoreConfig
from app.auth.util import validate_email
from app.exam.exam_config import ExamConfig
from app.models.analysis import *
from app.models.exam import QuestionModel
from app.models.user import UserModel
from . import admin, util
from .algorithm import OptimizeAlgorithm
from app.admin.util import *


@admin.route('/score/question', methods=['GET'])
def get_score_of_all_questions():
    """获取各题目平均分的成绩情况

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_questions')

    all_answers = AnalysisModel.objects().order_by('question_num')
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = QuestionNumMapper()
    result = generate_result_from_dict(mapper.map_answers(all_answers), 'questionId')
    return jsonify(errors.success({'result': result}))


@admin.route('/score/question/<id>', methods=['GET'])
def get_score_of_specific_questions(id):
    """获取某题目的成绩情况

    :param id: 题号ID
    :return: 该问题的成绩情况
    """
    current_app.logger.info('get_score_of_specific_questions   ' + id)

    cur_question = QuestionModel.objects(q_id=id).first()
    if not cur_question:
        return jsonify(errors.Score_criteria_not_exist)

    all_answers = AnalysisModel.objects(question_num=id).order_by('date')
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = DateMapper()
    result_by_date = generate_result_from_dict(mapper.map_answers(all_answers), 'date')

    result_all = []
    for answer in all_answers:
        result_all.append(generate_total_score(answer['score_key'], answer['score_detail']))

    return jsonify(errors.success({
        'resultByDate': result_by_date,
        'allResult': result_all
    }))


@admin.route('/score/user', methods=['GET'])
def get_score_of_all_users():
    """获取各用户平均分的成绩情况

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_users')

    all_answers = AnalysisModel.objects()
    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    mapper = UserMapper()
    result = generate_result_from_dict(mapper.map_answers(all_answers), 'username')

    # map_answers_by_user() 返回的结果中 key 为 ObjectId，需要改为 email / phone
    for item in result:
        cur_user_id = item['username']
        cur_user = UserModel.objects(id=cur_user_id).first()

        if cur_user:
            cur_username = cur_user['email'] if cur_user['email'] else cur_user['phone']
        else:
            cur_username = cur_user_id.__str__() + ScoreConfig.DEFAULT_USER_EMAIL

        item['username'] = cur_username
    return jsonify(errors.success({'result': result}))


@admin.route('/score/user/<username>', methods=['GET'])
def get_score_of_specific_users(username):
    """获取某用户的成绩情况

    :param username: 用户邮箱
    :return: 该用户的成绩情况
    """
    current_app.logger.info('get_score_of_specific_users   ' + username)

    if '@' in username:
        # 邮箱登录
        email = username
        if not validate_email(email):
            return jsonify(errors.Params_error)
        if ScoreConfig.DEFAULT_USER_EMAIL in username:
            # 默认邮箱，通过主键查询
            user_object_id = username[:-16]
            all_answers = AnalysisModel.objects(user=user_object_id).order_by('date')
        else:
            # 真实邮箱
            cur_user = UserModel.objects(email=username).first()
            if not cur_user:
                return jsonify(errors.Score_criteria_not_exist)
            all_answers = AnalysisModel.objects(user=cur_user['id']).order_by('date')
    else:
        # 手机号登录
        cur_user = UserModel.objects(phone=username).first()
        if not cur_user:
            return jsonify(errors.Score_criteria_not_exist)
        all_answers = AnalysisModel.objects(user=cur_user['id']).order_by('date')

    if len(all_answers) == 0:
        return jsonify(errors.Score_no_data)

    date_mapper = DateMapper()
    result_by_date = generate_result_from_dict(date_mapper.map_answers(all_answers), 'date')

    question_id_mapper = QuestionNumMapper()
    result_by_qid = generate_result_from_dict(question_id_mapper.map_answers(all_answers), 'questionId')
    # 按照 q_id 排序
    result_by_qid.sort(key=sort_by_question_id)

    result_all = []
    for answer in result_by_qid:
        result_all.append({'questionId': answer['questionId'], 'totalScore': answer['totalScore']})

    return jsonify(errors.success({
        'resultByDate': result_by_date,
        'allResult': result_all
    }))



