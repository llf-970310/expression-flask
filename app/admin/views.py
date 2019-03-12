#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-26

from . import admin
from flask_login import login_required, current_user
import random

from app.exam.util import *
from app.models.user import UserModel
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify, session
from flask_login import current_user
from celery_tasks import analysis_main_12, analysis_main_3
import datetime
import shutil
import os
import traceback


@admin.route('/admin-login',methonds='POST')
def admin_login():
    user_name = request.form.get("adminName")
    password = request.form.get("adminPassword")
    users = UserModel.objects(Q(student_id=user_name) & Q(password=password))
    if len(users) == 0:
        msg={"needDisplay": True, "tip": "用户名或密码错误"}
        return jsonify(errors.error(msg))
    user = users[0]
    user.last_login_time = datetime.datetime.utcnow()
    # 设置session
    session["user_name"] = user_name
    session["student_id"] = user_name
    session["question_num"] = 0
    session["new_test"] = True
    session["user_id"] = user.id.__str__()
    session["test_id"] = DefaultValue.test_id
    session["admin_login"] = True
    current_app.logger.info("[INFO] admin login, name: %s, password: %s." % (user_name, password))
    # print("[INFO] admin login, name: %s, password: %s." % (user_name, password))
    resp = {"status": "Success"}
    return jsonify(errors.success(resp))


@admin.route('/admin-get-question',methods='POST')
def admin_get_question():
    if not session.get("admin_login"):
        resp={"needDisplay": True, "tip": "请以管理员身份登陆"}
        return jsonify(errors.error(resp))
    question_id = int(request.form.get("questionId"))
    questions = QuestionModel.objects(q_id=question_id)
    if len(questions) == 0:
        resp={"needDisplay": True, "tip": "没有此题号"}
        return jsonify(errors.error(resp))
    question = questions[0]
    if question["q_type"] != 2:
        resp={"needDisplay": True, "tip": "暂时只支持题型2"}
        return jsonify(errors.error(resp))

    # 生成测试
    test = CurrentTestModel()
    test.user_id = session.get("user_id")
    test.test_start_time = datetime.datetime.utcnow()
    q_current = CurrentQuestionEmbed(q_id=question.id.__str__(), q_type=question.q_type, q_text=question.text,
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


@admin.route('/admin-get-result',methos='POST')
def admin_get_result():
    if not session.get("admin_login"):
        return jsonify(errors.Admin_status_login)
    # print("[INFO] admin_get_result: user_name: " + request.session.get("user_name", "NO USER"))
    current_app.logger.info("admin_get_result: user_name: " + session.get("user_name", "NO USER"))
    current_test_id = session.get("test_id")
    tests = CurrentTestModel.objects(id=current_test_id)
    if len(tests) == 0:
        # print("[ERROR] upload_file ERROR: No Tests!, test_id: %s" % current_test_id)
        current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % current_test_id)
        return jsonify(errors.Exam_not_exist)
    questions = tests[0]['questions']

    if len(questions) == 0:
        # print("[ERROR] upload_file ERROR: No Questions!, test_id: %s" % current_test_id)
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
        return jsonify(errors.Music_deal_failed)
    else:
        result = json.dumps({"status": "InProcess"})

    return jsonify(errors.success(result))


@admin.route('/admin-get-result-stub',methods='POST')
def admin_get_result_stub():
    if not session.get("admin_login"):
        return jsonify(errors.Admin_status_login)
    question = CurrentTestModel.objects(id="5c0cdeafdd626279845e0560")[0]["questions"]["1"]
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
    return jsonify(errors.success(result))