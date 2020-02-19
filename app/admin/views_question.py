import json

from flask import request, current_app, jsonify
from flask_login import current_user

from app import errors
from app.models.exam import *
from app.models.origin import *
from . import admin, util
from . import mock_data
from .question_generator import generator

wordbase_generator = generator.WordbaseGenerator()


@admin.route('/generate-keywords', methods=['POST'])
def generate_wordbase_by_text():
    """根据原文重新生成关键词

    :return: 分析后的关键词
    """
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    if not current_user.is_admin():
        return jsonify(errors.Admin_login_required)

    text = request.form.get('text')
    return jsonify(errors.success(wordbase_generator.generate_wordbase(text)))


@admin.route('/question-type-two', methods=['GET'])
def get_all_type_two_questions():
    """获取所有第二种类型的题目

    :return: 所有第二种类型的题目题目，可直接展示
    """
    (page, size) = util.get_page_and_size_from_request_args(request.args)
    current_app.logger.info('get_all_type_two_questions  page = %d, size = %d', page, size)

    all_questions_num = len(QuestionModel.objects(q_type=2))

    temp_question_query_max = page * size
    question_query_max = all_questions_num if temp_question_query_max > all_questions_num \
        else temp_question_query_max
    questions = QuestionModel.objects(q_type=2)[((page - 1) * size):question_query_max].order_by('q_id')

    data = []
    for question in questions:
        data.append({
            "questionId": question['q_id'],
            "rawText": question['text'],
            "keywords": util.array2str(question['wordbase']['keywords'], 2),
            "detailwords": util.array2str(question['wordbase']['detailwords'], 3),
            "inOptimize": question['in_optimize'],
            "lastOpDate": question['last_optimize_time'],
            "optimized": question['auto_optimized'],
        })
    return jsonify(errors.success({"count": all_questions_num, "questions": data}))


@admin.route('/questions', methods=['GET'])
def get_all_questions():
    """获取所有题目 TODO

    :return: 所有题目，可直接展示
    """
    (page, size) = util.get_page_and_size_from_request_args(request.args)
    return jsonify(errors.success(mock_data.questions))


@admin.route('/question/<id>', methods=['GET'])
def get_question(id):
    """获取问题详情

    :param id: 问题ID
    :return:  该问题详情
    """
    current_app.logger.info('q_id = ' + id)
    result_question = QuestionModel.objects(q_id=id).first()

    # 要获取的题目不存在
    if not result_question:
        return jsonify(errors.Question_not_exist)

    # wrap question
    context = {
        "questionId": result_question['q_id'],
        "rawText": result_question['text'],
        "keywords": result_question['wordbase']['keywords'],
        "detailwords": result_question['wordbase']['detailwords'],
    }
    return jsonify(errors.success(context))


@admin.route('/question/<id>', methods=['DELETE'])
def del_question(id):
    """删除特定问题

    :param id: 问题ID
    :return:  该问题详情
    """
    # 检验是否有权限删除题目
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    if not current_user.is_admin():
        return jsonify(errors.Admin_login_required)

    current_app.logger.info('q_id = ' + id)
    to_delete_question = QuestionModel.objects(q_id=id).first()

    # 要获取的题目不存在
    if not to_delete_question:
        return jsonify(errors.Question_not_exist)
    else:
        to_delete_question.delete()
        return jsonify(errors.success())


@admin.route('/question-from-pool', methods=['GET'])
def get_question_from_pool():
    """获取题库中题目

    :return: 题库中的某道题
    """
    result_question = OriginTypeTwoQuestionModel.objects().first()

    # 题库导入时无题目
    if not result_question:
        return jsonify(errors.Origin_question_no_more)

    context = {
        "rawText": result_question['text'],
        "keywords": result_question['wordbase']['keywords'],
        "detailwords": result_question['wordbase']['detailwords'],
        "origin": result_question['origin'],
        "url": result_question['url'],
    }
    return jsonify(errors.success({'question': context, 'id': result_question['q_id']}))


@admin.route('/question-from-pool', methods=['DELETE'])
def delete_specific_question_from_pool():
    """
    删除题库中题目
    """
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    if not current_user.is_admin():
        return jsonify(errors.Admin_login_required)

    id = request.form.get('idInPool')

    origin_question = OriginTypeTwoQuestionModel.objects(q_id=id).first()
    if not origin_question:
        return jsonify(errors.Question_not_exist)

    origin_question.delete()
    return jsonify(errors.success())


@admin.route('/question', methods=['POST'])
def post_new_question():
    """新建一个问题

    :return:
    """
    # 提取参数
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    if not current_user.is_admin():
        return jsonify(errors.Admin_login_required)

    is_from_pool = request.form.get('isFromPool')
    id_in_pool = request.form.get('idInPool')
    question_data_raw_text = request.form.get('data[rawText]')
    question_wordbase = {
        "keywords": json.loads(request.form.get('data[keywords]')),
        "detailwords": json.loads(request.form.get('data[detailwords]')),
    }

    if util.str_to_bool(is_from_pool):
        # 词库导入时，需要删除原项，即从 origin_questions 中删除
        origin_question = OriginTypeTwoQuestionModel.objects(q_id=id_in_pool).first()
        if not origin_question:
            return jsonify(errors.Question_not_exist)
        else:
            origin_question.delete()

    # 进入 questions 的 q_id
    next_q_id = util.get_next_available_question_id()
    current_app.logger.info('next_q_id: ' + next_q_id.__str__())
    # 插入 questions，初始化关键词权重 weights
    new_question = QuestionModel(
        q_type=2,
        level=5,
        text=question_data_raw_text,
        wordbase=question_wordbase,
        weights=util.reset_question_weights(question_wordbase),
        q_id=next_q_id
    )
    new_question.save()
    return jsonify(errors.success())


@admin.route('/question', methods=['PUT'])
def modify_question():
    """修改一个问题

    :return:
    """
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    if not current_user.is_admin():
        return jsonify(errors.Admin_login_required)

    id = request.form.get('id')
    question_data_raw_text = request.form.get('data[rawText]')
    question_wordbase = {
        "keywords": json.loads(request.form.get('data[keywords]')),
        "detailwords": json.loads(request.form.get('data[detailwords]')),
    }

    question = QuestionModel.objects(q_id=id).first()
    if not question:
        return jsonify(errors.Question_not_exist)

    # 修改关键词的同时需要重置关键词权重
    question.update(
        text=question_data_raw_text,
        wordbase=question_wordbase,
        weights=util.reset_question_weights(question_wordbase)
    )

    return jsonify(errors.success())



