from . import admin, util, analysis
from app.admin.admin_config import PaginationConfig
from app.exam.util import *
from app import errors
from app.models.exam import *
from app.models.origin import *
from flask import request, current_app, jsonify, session
from . import mock_data
import json


@admin.route('/question-type-two', methods=['GET'])
def get_all_type_two_questions():
    """获取所有第二种类型的题目

    :return: 所有第二种类型的题目题目，可直接展示
    """
    (page, size) = get_page_and_size_from_request_args(request.args)
    current_app.logger.info('get_all_type_two_questions  page = %d, size = %d', page, size)

    questions = QuestionModel.objects(q_type=2)[((page - 1) * size):size].order_by('q_id')
    all_questions_num = len(QuestionModel.objects(q_type=2))

    data = []
    for question in questions:
        data.append({
            "questionId": question['q_id'],
            "rawText": question['text'],
            "keywords": array2str(question['wordbase']['keywords'], 2),
            "mainwords": array2str(question['wordbase']['mainwords'], 2),
            "detailwords": array2str(question['wordbase']['detailwords'], 3),
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
    (page, size) = get_page_and_size_from_request_args(request.args)
    return jsonify(errors.success(mock_data.questions))


def get_page_and_size_from_request_args(args):
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


def array2str(array, level):
    """

    :param array: 需要展示的的原数组
    :param level: 数组需要遍历的层级
    :return: 可直接展示的 word 的数组
    """
    if level == 2:
        string = "「"
        for i in range(0, len(array)):
            split = '，'
            string += ('「' + split.join(array[i]) + '」')
            if i < len(array) - 1:
                string += '，'
        string += '」'
    elif level == 3:
        string = '「'
        for i in range(0, len(array)):
            string += "「"
            for j in range(0, len(array[i])):
                split = '，'
                string += ('「' + split.join(array[i][j]) + '」')
                if j < len(array[i]) - 1:
                    string += '，'
            string += '」'
            if i < len(array) - 1:
                string += '，'
        string += '」'
    else:
        string = ''
    return string


@admin.route('/question/<id>', methods=['GET'])
def get_question(id):
    """获取问题详情 TODO

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
        "mainwords": result_question['wordbase']['mainwords'],
        "detailwords": result_question['wordbase']['detailwords'],
    }
    return jsonify(errors.success(context))


@admin.route('/question-from-pool', methods=['GET'])
def get_question_from_pool():
    """获取题库中题目

    :return: 题库中的某道题
    """
    result_question = OriginQuestionModel.objects().first()

    # 题库导入时无题目
    if not result_question:
        return jsonify(errors.Origin_question_no_more)

    context = {
        "rawText": result_question['text'],
        "keywords": result_question['wordbase']['keywords'],
        "mainwords": result_question['wordbase']['mainwords'],
        "detailwords": result_question['wordbase']['detailwords'],
    }
    return jsonify(errors.success({'question': context, 'id': result_question['q_id']}))


@admin.route('/question', methods=['POST'])
def post_new_question():
    """新建一个问题

    :return:
    """
    # 提取参数
    is_from_pool = request.form.get('isFromPool')
    id_in_pool = request.form.get('idInPool')
    question_data_raw_text = request.form.get('data[rawText]')
    question_wordbase = {
        "keywords": json.loads(request.form.get('data[keywords]')),
        "mainwords": json.loads(request.form.get('data[mainwords]')),
        "detailwords": json.loads(request.form.get('data[detailwords]')),
    }

    if util.str_to_bool(is_from_pool):
        # 词库导入时，需要删除原项，即从 origin_questions 中删除
        origin_question = OriginQuestionModel.objects(q_id=id_in_pool).first()
        if not origin_question:
            return jsonify(errors.Question_not_exist)
        else:
            origin_question.delete()

    # 进入 questions 的 q_id
    next_q_id = get_next_available_question_id()
    current_app.logger.info('next_q_id: ' + next_q_id.__str__())
    # 插入 questions
    new_question = QuestionModel(
        q_type=2,
        level=5,
        text=question_data_raw_text,
        wordbase=question_wordbase,
        q_id=next_q_id
    )
    new_question.save()
    return jsonify(errors.success())


def get_next_available_question_id():
    """获取当前题目 question 中最大的题号

    :return: 当前最大题号
    """
    max_question = QuestionModel.objects().order_by('-q_id').limit(1).first()
    return max_question['q_id'] + 1


@admin.route('/question', methods=['PUT'])
def modify_question():
    """修改一个问题

    :return:
    """
    id = request.form.get('id')
    question_data_raw_text = request.form.get('data[rawText]')
    question_wordbase = {
        "keywords": json.loads(request.form.get('data[keywords]')),
        "mainwords": json.loads(request.form.get('data[mainwords]')),
        "detailwords": json.loads(request.form.get('data[detailwords]')),
    }

    question = QuestionModel.objects(q_id=id).first()
    if not question:
        return jsonify(errors.Question_not_exist)

    question.update(
        text=question_data_raw_text,
        wordbase=question_wordbase,
    )

    return jsonify(errors.success())
