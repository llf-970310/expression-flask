import json
from functools import reduce

from flask import request, current_app, jsonify
from flask_login import current_user

from app import errors
from app.admin.admin_config import PaginationConfig
from app.models.question import QuestionModel
from app.models.origin import *
from . import admin, util
from .question_generator import generator
from app.auth.util import admin_login_required

wordbase_generator = generator.WordbaseGenerator()


@admin.route('/generate-keywords', methods=['POST'])
@admin_login_required
def generate_wordbase_by_text():
    """根据原文重新生成关键词

    :return: 分析后的关键词
    """
    text = request.form.get('text')
    return jsonify(errors.success(wordbase_generator.generate_wordbase(text)))


@admin.route('/question-type-two', methods=['GET'])
@admin_login_required
def get_all_type_two_questions():
    """获取所有第二种类型的题目

    :return: 所有第二种类型的题目题目，可直接展示
    """
    (page, size) = __get_page_and_size_from_request_args(request.args)
    current_app.logger.info('get_all_type_two_questions  page = %d, size = %d', page, size)

    all_questions_num = len(QuestionModel.objects(q_type=2))

    temp_question_query_max = page * size
    question_query_max = all_questions_num if temp_question_query_max > all_questions_num \
        else temp_question_query_max
    questions = QuestionModel.objects(q_type=2)[((page - 1) * size):question_query_max].order_by('index')

    data = []
    for question in questions:
        data.append({
            "questionId": question['index'],
            "rawText": question['text'],
            "keywords": util.array2str(question['wordbase']['keywords'], 2),
            "detailwords": util.array2str(question['wordbase']['detailwords'], 3),
            "inOptimize": question['in_optimize'],
            "lastOpDate": question['last_optimize_time'],
            "optimized": question['auto_optimized'],
            "upCount": question.up_count,
            "downCount": question.down_count,
            "usedTimes": question.used_times,
        })
    return jsonify(errors.success({"count": all_questions_num, "questions": data}))


def __get_page_and_size_from_request_args(args):
    """从请求中获得参数

    :param args: request.args get请求的参数
    :return: get请求中的page、size参数组成的元组
    """
    page = args.get('page')
    size = args.get('size')

    # 参数小于0不合法，日志记录
    if page and int(page) < 0:
        current_app.logger.info('page is not applicable, and page = %d', page)
    if size and int(size) < 0:
        current_app.logger.info('size is not applicable, and size = %d', size)

    # 提供默认参数
    if page == None or page == '' or int(page) < 0:
        page = PaginationConfig.DEFAULT_PAGE
    else:
        page = int(page)

    if size == None or size == '' or int(size) < 0:
        size = PaginationConfig.DEFAULT_SIZE
    else:
        size = int(size)

    current_app.logger.info('page = %d, size = %d', page, size)
    return (page, size)


@admin.route('/question/<index>', methods=['GET'])
@admin_login_required
def get_question(index):
    """获取问题详情

    :param index: 问题ID
    :return:  该问题详情
    """
    current_app.logger.info('index:' + index)
    result_question = QuestionModel.objects(index=index).first()

    # 要获取的题目不存在
    if not result_question:
        return jsonify(errors.Question_not_exist)

    # wrap question
    context = {
        "questionId": result_question['q_id'],
        "rawText": result_question['text'],
        "keywords": result_question['wordbase']['keywords'],
        "detailwords": result_question['wordbase']['detailwords'],
        "upCount": result_question.up_count,
        "downCount": result_question.down_count,
        "usedTimes": result_question.used_times,
    }
    return jsonify(errors.success(context))


@admin.route('/question/<index>', methods=['DELETE'])
@admin_login_required
def del_question(index):
    """删除特定问题

    :param index: 问题ID
    :return:  该问题详情
    """
    # 检验是否有权限申请邀请码
    current_app.logger.info('delete question, index:' + index)
    to_delete_question = QuestionModel.objects(index=index).first()

    # 要获取的题目不存在
    if not to_delete_question:
        return jsonify(errors.Question_not_exist)
    else:
        to_delete_question.delete()
        return jsonify(errors.success())


@admin.route('/question-from-pool', methods=['GET'])
@admin_login_required
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
@admin_login_required
def delete_specific_question_from_pool():
    """
    删除题库中题目
    """
    id = request.form.get('idInPool')

    origin_question = OriginTypeTwoQuestionModel.objects(q_id=id).first()
    if not origin_question:
        return jsonify(errors.Question_not_exist)

    origin_question.delete()
    return jsonify(errors.success())


@admin.route('/question', methods=['POST'])
@admin_login_required
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
    next_q_index = __get_next_available_question_index()
    current_app.logger.info('next_q_index: ' + next_q_index.__str__())
    # 插入 questions，初始化关键词权重 weights
    new_question = QuestionModel(
        q_type=2,
        level=5,
        text=question_data_raw_text,
        wordbase=question_wordbase,
        weights=__reset_question_weights(question_wordbase),
        index=next_q_index
    )
    new_question.save()
    return jsonify(errors.success())


def __get_next_available_question_index():
    """获取当前题目 question 中最大的题号

    :return: 当前最大题号
    """
    max_question = QuestionModel.objects().order_by('-index').limit(1).first()
    return max_question['index'] + 1


@admin.route('/question', methods=['PUT'])
@admin_login_required
def modify_question():
    """修改一个问题

    :return:
    """

    index = request.form.get('id')  # todo: change to REST api and change name 'id' to 'index'
    question_data_raw_text = request.form.get('data[rawText]')
    question_wordbase = {
        "keywords": json.loads(request.form.get('data[keywords]')),
        "detailwords": json.loads(request.form.get('data[detailwords]')),
    }

    question = QuestionModel.objects(index=index).first()
    if not question:
        return jsonify(errors.Question_not_exist)

    # 修改关键词的同时需要重置关键词权重
    question.update(
        text=question_data_raw_text,
        wordbase=question_wordbase,
        weights=__reset_question_weights(question_wordbase)
    )

    return jsonify(errors.success())


def __reset_question_weights(wordbase):
    """
    1。 重置问题关键词的权重：权重的数量等于词的数量加一，每个词的权重=100/权重的数量
    2。 重置权重的击中次数为0
    """
    weights = {}
    len_keywords = len(wordbase['keywords'])
    len_detailwords = len(reduce(lambda x, y: x + y, wordbase['detailwords']))

    # 重置问题关键词的权重
    key_init = 100 / (len_keywords + 1)
    detail_init = 100 / (len_detailwords + 1)
    weights['key'] = [key_init for i in range(len_keywords + 1)]
    weights['detail'] = [detail_init for i in range(len_detailwords + 1)]

    # 重置权重的击中次数为0
    weights['key_hit_times'] = [0 for i in range(len_keywords)]
    weights['detail_hit_times'] = [0 for i in range(len_detailwords)]
    return weights
