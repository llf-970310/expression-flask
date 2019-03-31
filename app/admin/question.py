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


@admin.route('/questions', methods=['GET'])
def get_all_questions():
    """获取所有题目 TODO

    :return: 所有题目，可直接展示
    """
    page = request.args.get('page')
    size = request.args.get('size')

    if page == None or page == '':
        page = QuestionConfig.default_page
    else:
        page = int(page)

    if size == None or size == '':
        size = QuestionConfig.default_size
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
    return jsonify(errors.success(mock_data.questionDB[index]))


@admin.route('/question-from-pool', methods=['GET'])
def get_question_from_pool():
    """获取题库中题目

    :return: 题库中的某道题
    """
    return jsonify(errors.success({'question': mock_data.questionFromPool, 'id': 32}))


@admin.route('/question', methods=['POST'])
def post_new_question():
    """新建一个问题 TODO

    :return:
    """
    isFromPool = request.form.get('isFromPool')
    idInPool = request.form.get('idInPool')
    questionDataRawText = request.form.get('data[rawText]')
    questionDataKeywords = json.loads(request.form.get('data[keywords]'))
    questionDataMainwords = json.loads(request.form.get('data[mainwords]'))
    questionDataDetailwords = json.loads(request.form.get('data[detailwords]'))

    current_app.logger.info(isFromPool)
    current_app.logger.info(idInPool)
    current_app.logger.info(questionDataRawText)
    current_app.logger.info(questionDataKeywords)
    current_app.logger.info(questionDataMainwords)
    current_app.logger.info(questionDataDetailwords)

    return jsonify(errors.success())


@admin.route('/question', methods=['PUT'])
def modify_question():
    """修改一个问题 TODO

    :return:
    """
    id = request.form.get('id')
    questionDataRawText = request.form.get('data[rawText]')
    questionDataKeywords = json.loads(request.form.get('data[keywords]'))
    questionDataMainwords = json.loads(request.form.get('data[mainwords]'))
    questionDataDetailwords = json.loads(request.form.get('data[detailwords]'))

    current_app.logger.info(id)
    current_app.logger.info(questionDataRawText)
    current_app.logger.info(questionDataKeywords)
    current_app.logger.info(questionDataMainwords)
    current_app.logger.info(questionDataDetailwords)

    return jsonify(errors.success())
