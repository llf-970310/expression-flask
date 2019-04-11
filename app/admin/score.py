from . import admin, algorithm
from app.exam.util import *
from app.exam.config import ExamConfig
from app.admin.config import ScoreConfig
from app import errors
from app.models.user import UserModel
from app.models.analysis import *
from flask import request, current_app, jsonify, session
import datetime
import json
import random
import math
import datetime


@admin.route('/score/question', methods=['GET'])
def get_score_of_all_questions():
    """获取各题目平均分的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_questions')
    result = []

    answers_by_question_num = map_answers_by_question_num(AnalysisModel.objects().order_by('question_num'))
    for question_num in answers_by_question_num:
        cur_answers = answers_by_question_num[question_num]
        detail_scores = [cur_answer['detail'] for cur_answer in cur_answers]
        key_scores = [cur_answer['key'] for cur_answer in cur_answers]

        key_score = algorithm.analysis_score(key_scores, ExamConfig.full_score)['mean']
        detail_score = algorithm.analysis_score(detail_scores, ExamConfig.full_score)['mean']
        result.append({
            'questionId': question_num,
            'mainScore': key_score,
            'detailScore': detail_score,
            'totalScore': key_score * ExamConfig.key_percent + detail_score * ExamConfig.detail_percent
        })
    return jsonify(errors.success({'result': result}))


def map_answers_by_question_num(answers):
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


@admin.route('/score/question/<id>', methods=['GET'])
def get_score_of_specific_questions(id):
    """获取某题目的成绩情况 TODO

    :param id: 题号ID
    :return: 该问题的成绩情况
    """
    current_app.logger.info('get_score_of_specific_questions   ' + id)

    base_date = datetime.date(2018, 1, 1)
    date_delta = datetime.timedelta(days=1)
    result = []
    for i in range(365):
        main_score = math.floor(random.random() * 100)
        detail_score = math.floor(random.random() * 100)
        result.append({
            'date': base_date.strftime("%Y-%m-%d"),
            'mainScore': main_score,
            'detailScore': detail_score,
            'totalScore': main_score * 0.7 + detail_score * 0.3
        })

        base_date = base_date + date_delta
    return jsonify(errors.success({'result': result}))


@admin.route('/score/user', methods=['GET'])
def get_score_of_all_users():
    """获取各用户平均分的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_users')
    result = []

    answers_by_user = map_answers_by_user(AnalysisModel.objects())
    for user in answers_by_user:
        cur_answers = answers_by_user[user]
        detail_scores = [cur_answer['detail'] for cur_answer in cur_answers]
        key_scores = [cur_answer['key'] for cur_answer in cur_answers]

        key_score = algorithm.analysis_score(key_scores, ExamConfig.full_score)['mean']
        detail_score = algorithm.analysis_score(detail_scores, ExamConfig.full_score)['mean']

        cur_user = UserModel.objects(id=user).first()
        cur_user_email = cur_user if cur_user else ScoreConfig.DEFAULT_USER_EMAIL + user
        result.append({
            'userEmail': cur_user_email,
            'mainScore': key_score,
            'detailScore': detail_score,
            'totalScore': key_score * ExamConfig.key_percent + detail_score * ExamConfig.detail_percent
        })
    return jsonify(errors.success({'result': result}))


def map_answers_by_user(answers):
    """将所有回答结果按照题号对应

    :param answers: 所有的回答
    :return: key 为题号，value 为相应的 {key, detail} 得分的字典
    """
    res = {}
    for answer in answers:
        cur_user = answer['user']
        if cur_user in res:
            res[cur_user].append({'key': answer['score_key'], 'detail': answer['score_detail']})
        else:
            res[cur_user] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
    return res


@admin.route('/score/user/<user_email>', methods=['GET'])
def get_score_of_specific_users(user_email):
    """获取某用户的成绩情况 TODO

    :param user_email: 用户邮箱
    :return: 该用户的成绩情况
    """
    current_app.logger.info('get_score_of_specific_users   ' + user_email)

    base_date = datetime.date(2018, 1, 1)
    date_delta = datetime.timedelta(days=1)
    result = []
    for i in range(365):
        main_score = math.floor(random.random() * 100)
        detail_score = math.floor(random.random() * 100)
        result.append({
            'date': base_date.strftime("%Y-%m-%d"),
            'mainScore': main_score,
            'detailScore': detail_score,
            'totalScore': main_score * 0.7 + detail_score * 0.3
        })

        base_date = base_date + date_delta
    return jsonify(errors.success({'result': result}))
