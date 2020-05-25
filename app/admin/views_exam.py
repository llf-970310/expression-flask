#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-26

import datetime
import json

from flask_login import current_user

from app.auth.util import admin_login_required
from app import errors
from app.models.exam import CurrentTestModel, CurrentQuestionEmbed
from app.models.question import QuestionModel
from flask import request, current_app, jsonify, session
from app.exam.exam_config import ExamConfig, QuestionConfig
from . import admin

# 这个文件貌似是给管理员刷题自测用的,现在前端没有使用


@admin.route('/admin-get-question', methods=['POST'])
@admin_login_required
def admin_get_question():
    question_index = int(request.form.get("questionId"))  # todo: change api and param name
    questions = QuestionModel.objects(index=question_index)
    if len(questions) == 0:
        resp = {"needDisplay": True, "tip": "没有此题号"}
        return jsonify(errors.error(resp))
    question = questions[0]
    if question["q_type"] != 2:
        resp = {"needDisplay": True, "tip": "暂时只支持题型2"}
        return jsonify(errors.error(resp))

    # 生成测试
    test = CurrentTestModel()
    test.user_id = str(current_user.id)
    test.test_start_time = datetime.datetime.utcnow()
    q_current = CurrentQuestionEmbed(q_id=str(question.id), q_type=question.q_type, q_text=question.text,
                                     wav_upload_url='', wav_temp_url='')
    test.questions = {"1": q_current}
    test.save()

    # 保存test id
    # print("[DEBUG] save test id in session when admin get question, test id: %s" % test.id.__str__())
    current_app.logger.debug("save test id in session when admin get question, test id: %s" % test.id.__str__())
    session["test_id"] = test.id.__str__()

    # wrap question
    context = {"questionType": question.q_type,
               "questionNumber": 1,
               "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
               "lastQuestion": True,
               "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
               "questionInfo": QuestionConfig.question_type_tip[question.q_type],
               "questionContent": question.text
               }
    return jsonify(errors.success(json.dumps(context)))


@admin.route('/admin-get-result', methods=['POST'])
@admin_login_required
def admin_get_result():
    current_app.logger.info("admin_get_result: user_name: " + session.get("user_name", "NO USER"))
    current_test_id = session.get("test_id")
    tests = CurrentTestModel.objects(id=current_test_id)
    if len(tests) == 0:
        current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % current_test_id)
        return jsonify(errors.Exam_not_exist)
    questions = tests[0]['questions']

    if len(questions) == 0:
        current_app.logger.error("upload_file ERROR: No Questions!, test_id: %s" % current_test_id)
        return jsonify(errors.Exam_not_exist)

    question = questions.get("1")
    if question['status'] == 'finished':
        score = question["score"]
        raw_question = QuestionModel.objects(id=question.q_id)[0]
        context = {"main": score["main"],
                   "detail": score["detail"],
                   "total": score["main"] * 0.7 + score["detail"] * 0.3,
                   "rcgText": question["feature"]["rcg_text"],
                   "text": question["q_text"],
                   "rcgKeyWords": question["feature"]["keywords"],
                   "keyWords": raw_question["wordbase"]["keywords"],
                   "rcgMainWords": question["feature"]["mainwords"],
                   "mainWords": raw_question["wordbase"]["mainwords"],
                   "rcgDetailWords": question["feature"]["detailwords"],
                   "detailWords": raw_question["wordbase"]["detailwords"]
                   }
        result = json.dumps({"status": "Success", "result": context})
    elif question['status'] not in ['none', 'url_fetched', 'handling']:
        return jsonify(errors.Audio_process_failed)
    else:
        result = json.dumps({"status": "InProcess"})

    return jsonify(errors.success(result))
