from . import admin
from app.exam.util import *
from app.models.user import UserModel
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify, session
from . import mock_data
import datetime
import json
import random
import math
import datetime


@admin.route('/score/question', methods=['GET'])
def get_score_of_all_questions():
    """获取所有题目的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_questions')

    result = []
    for i in range(200):
        main_score = math.floor(random.random() * 100)
        detail_score = math.floor(random.random() * 100)
        result.append({
            'questionId': i,
            'mainScore': main_score,
            'detailScore': detail_score,
            'totalScore': main_score * 0.7 + detail_score * 0.3
        })
    return jsonify(errors.success({'result': result}))


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
    """获取所有题目的成绩情况 TODO

    :return: 所有题目，可直接展示
    """
    current_app.logger.info('get_score_of_all_users')

    result = []
    for i in range(200):
        user_email = 'user' + str(math.floor(random.random() * 100)) + '@site.com'
        main_score = math.floor(random.random() * 100)
        detail_score = math.floor(random.random() * 100)
        result.append({
            'userEmail': user_email,
            'mainScore': main_score,
            'detailScore': detail_score,
            'totalScore': main_score * 0.7 + detail_score * 0.3
        })
    return jsonify(errors.success({'result': result}))


@admin.route('/score/user/<user_email>', methods=['GET'])
def get_score_of_specific_users(user_email):
    """获取某用户的成绩情况 TODO

    :param user_email: 用户邮箱
    :return: 该用户的成绩情况
    """
    current_app.logger.info('get_score_of_specific_users   ' +  user_email)

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