from . import admin
from app.exam.util import *
from app.models.user import UserModel
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify, session
from . import mock_data
import datetime
import json

from app.admin.config import QuestionConfig


@admin.route('/question-type-two', methods=['GET'])
def get_all_type_two_questions():
    questions = QuestionModel.objects(q_type=2)
    data = []
    for question in questions:
        data.append({
            "questionId": question['q_id'],
            "rawText": question['text'],
            "inOptimize": question['in_optimize'],
            "lastOpDate": question['last_optimize_time'],
            "optimized": question['auto_optimized'],
        })
    return jsonify(errors.success({"count": len(data), "questions": data}))


@admin.route('/questions', methods=['GET'])
def get_all_questions():
    """获取所有题目 TODO

    :return: 所有题目，可直接展示
    """
    page = request.args.get('page')
    size = request.args.get('size')

    if page == None or page == '':
        page = QuestionConfig.DEFAULT_PAGE
    else:
        page = int(page)

    if size == None or size == '':
        size = QuestionConfig.DEFAULT_SIZE
    else:
        size = int(size)

    current_app.logger.info('page = %d, size = %d', page, size)

    return jsonify(errors.success(mock_data.questions))


@admin.route('/question/<id>', methods=['GET'])
def get_question(id):
    """获取问题详情 TODO

    :param id: 问题ID
    :return:  该问题详情
    """
    import random
    index = int(id) % 4
    return jsonify(errors.success(mock_data.question_db[index]))


@admin.route('/question-from-pool', methods=['GET'])
def get_question_from_pool():
    """获取题库中题目

    :return: 题库中的某道题
    """
    return jsonify(errors.success({'question': mock_data.question_from_pool, 'id': 32}))


@admin.route('/question', methods=['POST'])
def post_new_question():
    """新建一个问题 TODO

    :return:
    """
    is_from_pool = request.form.get('isFromPool')
    id_in_pool = request.form.get('idInPool')
    question_data_raw_text = request.form.get('data[rawText]')
    question_data_keywords = json.loads(request.form.get('data[keywords]'))
    question_data_mainwords = json.loads(request.form.get('data[mainwords]'))
    question_data_detailwords = json.loads(request.form.get('data[detailwords]'))

    current_app.logger.info(is_from_pool)
    current_app.logger.info(id_in_pool)
    current_app.logger.info(question_data_raw_text)
    current_app.logger.info(question_data_keywords)
    current_app.logger.info(question_data_mainwords)
    current_app.logger.info(question_data_detailwords)

    return jsonify(errors.success())


@admin.route('/question', methods=['PUT'])
def modify_question():
    """修改一个问题 TODO

    :return:
    """
    id = request.form.get('id')
    question_data_raw_text = request.form.get('data[rawText]')
    question_data_keywords = json.loads(request.form.get('data[keywords]'))
    question_data_mainwords = json.loads(request.form.get('data[mainwords]'))
    question_data_detailwords = json.loads(request.form.get('data[detailwords]'))

    current_app.logger.info(id)
    current_app.logger.info(question_data_raw_text)
    current_app.logger.info(question_data_keywords)
    current_app.logger.info(question_data_mainwords)
    current_app.logger.info(question_data_detailwords)

    return jsonify(errors.success())
