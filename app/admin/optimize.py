from . import admin
from app.exam.util import *
from app.models.user import UserModel
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify, session
from . import mock_data
import datetime


@admin.route('/get-score-data', methods=['GET'])
def get_score_data():
    question_num = request.args.get('questionNum')
    print("get_score_data: questionNum: " + str(question_num))
    return jsonify(errors.success(mock_data.score_data))


@admin.route('/get-weight-data', methods=['GET'])
def get_weight_data():
    question_num = request.args.get("questionNum")
    print("get_weight_data: questionNum: " + str(question_num))
    return jsonify(errors.success(mock_data.weight_data))


@admin.route('/update-weight', methods=['POST'])
def update_weight():
    question_num = request.form.get('questionNum')
    weight = json.loads(request.form.get("weight"))

    print("update_weight: questionNum: " + str(question_num))
    print(weight)
    print(weight["keyWords"])
    print(type(weight["keyWords"][0]))

    return jsonify(errors.success(mock_data.weight_data))


@admin.route('/get-last-cost-data', methods=['GET'])
def get_last_cost_data():
    question_num = request.args.get("questionNum")
    print("get_last_cost_data: questionNum: " + str(question_num))
    return jsonify(errors.success(mock_data.cost_data))


@admin.route('/start-auto-optimize', methods=['POST'])
def start_auto_optimize():
    question_num = request.form.get("questionNum")
    settings = json.loads(request.form.get("settings"))
    print("start_auto_optimize: questionNum: " + str(question_num))
    print(settings)
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

