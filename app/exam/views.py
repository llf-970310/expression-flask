#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

from app.models.user import User
from . import exam
from app import errors
from .config import PathConfig, ExamConfig, QuestionConfig
from app.models.exam import *
from flask import request, current_app, jsonify, session
from flask_login import current_user
from celery_tasks import analysis_main_12, analysis_main_3
import datetime
import random
import shutil
import time
import os
import traceback


@exam.route('/upload-success-for-test', methods=['POST'])
def upload_success_for_test():
    upload_url = request.form.get("uploadUrl")
    q_type = int(request.form.get("questionType"))
    if not upload_url or not q_type:
        return jsonify(errors.Params_error)
    _temp_folder = "%sr%s" % (time.time(), random.randint(100, 1000))
    temp_url = '/'.join((PathConfig.audio_copy_temp_basedir, "batch_test", _temp_folder, os.path.basename(upload_url)))

    current_app.logger.info("upload_success_for_test: upload_url: " + upload_url)

    # 新建一个current
    current_test = CurrentTestModel()
    current_test.test_start_time = datetime.datetime.utcnow()
    q = QuestionModel.objects(q_type=q_type).order_by('used_times')[0]
    q_current = CurrentQuestionEmbed(q_id=q.id.__str__(), q_type=q.q_type, q_text=q.text, wav_upload_url='',
                                     wav_temp_url='')
    current_test.questions = {"1": q_current}
    current_test.save()

    try:
        # chdir should be 'xxx/expressiveness_server'
        dir_name = os.path.dirname(temp_url)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        shutil.copyfile(upload_url, temp_url)
    except Exception as e:
        current_app.logger.error(e)

    # change question state to handling
    current_test.questions['1'].status = 'handling'
    current_test.questions['1'].wav_upload_url = upload_url.lstrip('/expression')
    current_test.questions['1'].wav_temp_url = ''.join(('/expression/', temp_url))
    current_test.questions['1']['analysis_start_time'] = datetime.datetime.utcnow()
    current_test.save()

    try:
        if q.q_type == 3 or q.q_type == '3':
            ret = analysis_main_3.apply_async(args=(str(current_test.id), '1'), queue='for_q_type3', priority=10)
            # todo: store ret.id in redis for status query
        else:
            ret = analysis_main_12.apply_async(args=(str(current_test.id), '1'), queue='for_q_type12', priority=2)
            # todo: store ret.id in redis for status query
        current_app.logger.info("AsyncResult id: %s" % ret.id)
    except Exception as e:
        current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
        return jsonify(errors.exception({'Exception': str(e)}))
    resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": current_test.id.__str__(), "taskID": ret.id}
    return jsonify(errors.success(resp))


@exam.route('/get-result-for-test', methods=['POST'])
def get_result_for_test():
    test_id = request.form.get('testID')
    if not test_id or (len(test_id) != 12 and len(test_id) != 24):
        return jsonify(errors.Params_error)
    the_test = CurrentTestModel.objects(id=test_id).first()
    if the_test is None:
        return jsonify(errors.Exam_not_exist)
    try:
        question = the_test['questions']['1']
        status = question['status']
        start = question['analysis_start_time']
        end = question['analysis_end_time']
        if status != 'error':
            msg = {"status": status, "analysis_start_time": str(start), "analysis_end_time": str(end)}  # 转为str保证时间格式
            return jsonify(errors.success(msg))
        else:
            msg = {"status": status, "stack": question['stack'], "analysis_start_time": str(start),
                   "analysis_end_time": str(end)}
        return jsonify(errors.error(msg))
    except Exception as e:
        current_app.logger.error('get_result_for_test: %s' % traceback.format_exc())
        return jsonify(errors.exception({'Exception': str(e)}))


@exam.route('/next-question', methods=['POST'])
def next_question():
    if not current_user.is_authenticated:  # todo: 进一步检查是否有做题权限
        return jsonify(errors.Authorize_needed)
    # 关闭浏览器时session过期
    # session.set_expiry(0)
    # init question
    if session.get("new_test"):
        # 生成当前题目
        test_id = init_question(session["user_id"])
        if not test_id:
            return jsonify(errors.Init_exam_failed)
        else:
            session["test_id"] = test_id
        session["new_test"] = False
    # 获得下一题号
    next_question_num = int(request.form.get("nowQuestionNum", 0)) + 1
    session["question_num"] = next_question_num
    current_app.logger.info("net_question: username: %s, next_question_num: %s" % (
        session.get("user_name", "NO USER"), str(next_question_num)))
    # 如果超出最大题号，如用户多次刷新界面，则重定向到结果页面
    if next_question_num > ExamConfig.total_question_num:
        session["question_num"] = 0
        return jsonify(errors.redirect('/usr/result'))

    # 根据题号查找题目
    context = question_dealer(next_question_num, session["test_id"], session["user_id"])
    if not context:
        return jsonify(errors.Get_question_failed)
    return jsonify(errors.success({'data': context}))


def init_question(user_id):
    current_test = CurrentTestModel()
    user = User.objects(id=user_id).first()
    if user is None:
        current_app.logger.error("init_question ERROR: No Such User!")
        return False
    current_test.user_id = user_id
    current_test.test_start_time = datetime.datetime.utcnow()

    current_test.questions = {}
    temp_all_q_lst = []
    for t in ExamConfig.question_num_each_type.keys():
        temp_q_lst = []
        question_num_needed = ExamConfig.question_num_each_type[t]
        questions = QuestionModel.objects(q_type=t).order_by('used_times')  # 按使用次数倒序获得questions
        if ExamConfig.question_allow_repeat[t]:
            for q in questions:
                temp_q_lst.append(q)
                if len(temp_q_lst) >= question_num_needed:
                    break
        else:  # do Not use repeated questions
            q_history = set(user.questions_history)
            q_backup = []
            for q in questions:
                if q.id.__str__() not in q_history:
                    temp_q_lst.append(q)
                else:
                    q_backup.append(q)
                if len(temp_q_lst) >= question_num_needed:
                    break
            # 如果题目数量不够，用重复的题目补够
            if len(temp_q_lst) < question_num_needed:
                for q in q_backup:
                    temp_q_lst.append(q)
                    if len(temp_q_lst) >= question_num_needed:
                        break

            # 如果题目数量不够，报错
            if len(temp_q_lst) < question_num_needed:
                current_app.logger.error("init_question: Questions of Type %s Is Not Enough! "
                                         "need %s, but only has %s" % (t, question_num_needed, len(questions)))
                return False

        temp_all_q_lst += temp_q_lst

    for i in range(len(temp_all_q_lst)):
        q = temp_all_q_lst[i]
        q_current = CurrentQuestionEmbed(q_id=q.id.__str__(), q_type=q.q_type, q_text=q.text, wav_upload_url='',
                                         wav_temp_url='')
        current_test.questions.update({str(i + 1): q_current})
        q.update(inc__used_times=1)  # update

    # save
    current_test.save()
    return current_test.id.__str__()


def question_dealer(question_num, test_id, user_id):
    # get test
    test = CurrentTestModel.objects(id=test_id).first()
    if test is None:
        current_app.logger.error("question_generator ERROR: No Tests!, test_id: %s" % test_id)
        return False

    # wrap question
    question = test.questions[str(question_num)]
    context = {"questionType": question.q_type,
               "questionNumber": question_num,
               "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
               "lastQuestion": question_num == ExamConfig.total_question_num,
               "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
               "questionInfo": QuestionConfig.question_type_tip[question.q_type],
               "questionContent": question.q_text
               }

    # update and save
    question.status = 'url_fetched'
    test.current_q_num = question_num
    test.save()

    # log question id to user's historical questions
    user = User.objects(id=user_id).first()
    if user is None:
        current_app.logger.error("question_dealer: ERROR: user not find")
    user.questions_history.update({question.q_id: datetime.datetime.utcnow()})
    user.save()

    return context
