from . import admin, util
from .algorithm import OptimizeAlgorithm, GradientDescent, NormalEquation
from .analysis import Analysis
from app.admin.admin_config import OptimizeConfig
from app.exam.exam_config import ExamConfig
from app import errors
from app.models.question import QuestionModel
from app.models.analysis import AnalysisModel, OptimizeModel
from flask import request, jsonify
import datetime
import json
from functools import reduce


@admin.route('/get-score-data', methods=['GET'])
def get_score_data():
    # todo: 涉及到QuestionModel.index的引用太乱，需检查并改传入参数名为index，或者改参数使用_id
    question_num = request.args.get('questionNum')
    force = util.str_to_bool(request.args.get('force'))
    if force:
        question = QuestionModel.objects.filter(index=question_num).first()
        analysis = Analysis()
        analysis.re_analysis(question)
    print("get_score_data: questionNum: " + str(question_num))
    analysis_list = AnalysisModel.objects(question_num=question_num)
    if len(analysis_list) == 0:
        return jsonify(errors.success(OptimizeConfig.EMPTY_SCORE_DATA))
    data = {'key': [], 'detail': [], 'total': [], 'keyStatistic': {}, 'detailStatistic': {}, 'totalStatistic': {}}
    for a in analysis_list:
        if a["score_detail"] != 0 or a["score_key"] != 0:
            data['key'].append(a['score_key'])
            data['detail'].append(a['score_detail'])
            data['total'].append(
                a["score_detail"] * ExamConfig.detail_percent + a["score_key"] * ExamConfig.key_percent)
    algorithm = OptimizeAlgorithm()
    data['keyStatistic'] = algorithm.analysis_score(data['key'], ExamConfig.full_score)
    data['detailStatistic'] = algorithm.analysis_score(data['detail'], ExamConfig.full_score)
    data['totalStatistic'] = algorithm.analysis_score(data['total'], ExamConfig.full_score)
    return jsonify(errors.success(data))


@admin.route('/get-weight-data', methods=['GET'])
def get_weight_data():
    question_num = request.args.get("questionNum")
    print("get_weight_data: questionNum: " + str(question_num))
    question = QuestionModel.objects(index=question_num).first()
    if not question:
        return jsonify(errors.Question_not_exist)
    data = __question2weight(question)
    data['allHitTimes'] = len(AnalysisModel.objects(question_num=question_num))
    # return jsonify(errors.success(mock_data.weight_data))
    print(errors.success(data))
    return jsonify(errors.success(data))


@admin.route('/update-weight', methods=['POST'])
def update_weight():
    question_num = request.form.get('questionNum')
    weight = json.loads(request.form.get("weight"))

    print("update_weight: questionNum: " + str(question_num))
    print(weight)

    question = QuestionModel.objects(index=question_num).first()
    if not question:
        return jsonify(errors.Question_not_exist)
    question['weights']['key'] = weight['keyWeight']
    question['weights']['detail'] = weight['detailWeight']
    question['last_optimize_time'] = datetime.datetime.utcnow()
    question.save()
    # return jsonify(errors.success(mock_data.weight_data))
    return jsonify(errors.success(__question2weight(question)))


@admin.route('/get-last-cost-data', methods=['GET'])
def get_last_cost_data():
    question_num = request.args.get("questionNum")
    print("get_last_cost_data: questionNum: " + str(question_num))
    optimize_history = OptimizeModel.objects(question_num=question_num).order_by('-complete_time').first()
    if not optimize_history:
        return jsonify(errors.Optimize_not_exist)
    cost_history = []
    n = len(optimize_history['key_history_cost'])
    for i in range(OptimizeConfig.COST_POINT):
        index = int(i * n / OptimizeConfig.COST_POINT)
        cost_history.append({
            "itrTimes": index + 1,
            'keyCost': optimize_history['key_history_cost'][index],
            'detailCost': optimize_history['detail_history_cost'][index],
        })
    data = {
        "date": optimize_history['complete_time'],
        "finish": optimize_history['finish'],
        "costData": cost_history,
    }
    # return jsonify(errors.success(mock_data.cost_data))
    return jsonify(errors.success(data))


@admin.route('/start-auto-optimize', methods=['POST'])
def start_auto_optimize():
    question_num = request.form.get("questionNum")
    settings = json.loads(request.form.get("settings"))
    print("start_auto_optimize: questionNum: " + str(question_num))
    print(settings)

    # 重新计算某道题目所有人的击中向量
    question = QuestionModel.objects(index=question_num).first()
    if not question:
        return jsonify(errors.Question_not_exist)
    analysis = Analysis()
    analysis.re_analysis(question)
    # 根据击中向量优化参数
    analysis_list = AnalysisModel.objects(question_num=question_num).order_by('score_key')  # !!!从低到高排序
    if len(analysis_list) == 0:
        return jsonify(errors.success(OptimizeConfig.EMPTY_SCORE_DATA))
    key_hit_mat = []
    for a in analysis_list:
        key_hit_mat.append(a['key_hits'])
    detail_hit_mat = []
    analysis_list = analysis_list.order_by('score_detail')  # !!!从低到高排序
    for a in analysis_list:
        detail_hits = reduce(lambda x, y: x + y, a['detail_hits'])
        detail_hit_mat.append(detail_hits)

    algorithm = GradientDescent() if settings['algorithm'] == 'gradient' else NormalEquation()
    key_y = algorithm.get_gaussian_array(settings['keyMean'], settings['keySigma'], len(key_hit_mat))
    detail_y = algorithm.get_gaussian_array(settings['detailMean'], settings['detailSigma'], len(detail_hit_mat))
    settings['theta'] = question['weights']['key'] if settings['reuse'] else None
    # 调用优化方法
    key_theta, key_j = algorithm.optimize_param(key_hit_mat, key_y, settings)
    detail_theta, detail_j = algorithm.optimize_param(detail_hit_mat, detail_y, settings)
    # 存储优化结果
    question['weights']['key'] = key_theta
    question['weights']['detail'] = detail_theta
    question['last_optimize_time'] = datetime.datetime.utcnow()
    question['auto_optimized'] = True
    question.save()
    # 存储cost
    optimize = OptimizeModel()
    optimize['question_num'] = question_num
    optimize['wordbase'] = question['wordbase']
    optimize['weights'] = question['weights']
    optimize['key_history_cost'] = key_j
    optimize['detail_history_cost'] = detail_j
    optimize['complete_time'] = datetime.datetime.utcnow()
    optimize['finish'] = True
    optimize.save()
    return jsonify(errors.success())


@admin.route('/stop-auto-optimize', methods=['POST'])
def stop_auto_optimize():
    question_num = request.form.get("questionNum")
    print("stop_auto_optimize: questionNum: " + str(question_num))
    return jsonify(errors.success())


@admin.route('/refresh-auto-optimize', methods=['POST'])
def refresh_auto_optimize():
    question_num = request.form.get("questionNum")
    print("refresh_auto_optimize: questionNum: " + str(question_num))
    return jsonify(errors.success())


def __question2weight(question):
    detail = []
    for lst in question['wordbase']['detailwords']:
        detail += lst
    res = {
        'keyWords': question['wordbase']['keywords'],
        'keyWeight': question['weights']['key'],
        'keyHitTimes': question['weights']['key_hit_times'],
        'detailWords': detail,
        'detailWeight': question['weights']['detail'],
        'detailHitTimes': question['weights']['detail_hit_times']
    }
    return res
