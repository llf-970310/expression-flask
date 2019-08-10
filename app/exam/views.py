#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25
import random
import traceback

from flask import request, current_app, jsonify, session
from flask_login import current_user

from app import errors
from app.exam.util import *
from app.models.exam import *
from app.models.user import UserModel
from celery_tasks import analysis_main_12, analysis_main_3, analysis_wav_test
from . import exam
from .exam_config import PathConfig, ExamConfig, QuestionConfig, DefaultValue, Setting


@exam.route('/get-test-wav-info', methods=['POST'])
def get_test_wav_info():
    user_id = session.get('user_id')
    wav_test = WavTestModel()
    wav_test['text'] = QuestionConfig.test_text['content']
    wav_test['user_id'] = user_id
    wav_test.save()
    return jsonify(errors.success({
        "questionLimitTime": ExamConfig.question_limit_time[0],
        "readLimitTime": ExamConfig.question_prepare_time[0],
        "questionContent": wav_test['text'],
        "questionInfo": {
            "detail": QuestionConfig.test_text['detail'],
            "tip": QuestionConfig.test_text['tip'],
        },
        "test_id": wav_test.id.__str__()
    }))


@exam.route('/get-test-wav-url', methods=['POST'])
def get_test_wav_url():
    test_id = request.form.get('test_id')
    wav_test = WavTestModel.objects(id=test_id).first()
    if not wav_test:
        return jsonify(errors.success(errors.Test_not_exist))
    user_id = session.get('user_id')
    file_dir = '/'.join((PathConfig.audio_test_basedir, get_date_str('-'), user_id))
    _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
    file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
    wav_test['wav_upload_url'] = file_dir + '/' + file_name
    wav_test['file_location'] = 'BOS'
    wav_test.save()
    return jsonify(errors.success({
        "fileLocation": "BOS",
        "url": wav_test['wav_upload_url'],
        "test_id": wav_test.id.__str__()
    }))


@exam.route('/upload-test-wav-success', methods=['POST'])
def upload_test_wav_success():
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)
    test_id = request.form.get('test_id')
    wav_test = WavTestModel.objects(id=test_id).first()
    if not wav_test:
        return jsonify(errors.success(errors.Test_not_exist))
    wav_test['result']['status'] = 'handling'
    wav_test.save()
    try:
        ret = analysis_wav_test.apply_async(args=[test_id], queue='q_pre_test', priority=20)
        current_app.logger.info("AsyncResult id: %s" % ret.id)
    except Exception as e:
        current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
        return jsonify(errors.exception({'Exception': str(e)}))
    return jsonify(errors.success())


@exam.route('/get_test_result', methods=['POST'])
def get_test_result():
    test_id = request.form.get('test_id')
    wav_test = WavTestModel.objects(id=test_id).first()
    if not wav_test:
        return jsonify(errors.success(errors.Test_not_exist))
    if wav_test['result']['status'] == 'handling':
        return jsonify(errors.success(errors.WIP))
    elif wav_test['result']['status'] == 'finished':
        return jsonify(errors.success({"qualityIsOk": len(wav_test['result']['feature']['rcg_text']) >= len(
            wav_test['text']) * 0.6, "canRcg": True}))
    else:
        return jsonify(errors.success({"canRcg": False, "qualityIsOk": False}))


@exam.route('/get-upload-url', methods=['POST'])
def get_upload_url():
    # get question number
    question_num = int(request.form.get("nowQuestionNum"))
    # get test
    test_id = session.get("test_id", DefaultValue.test_id)
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        # print("[ERROR] get_upload_url ERROR: No Tests!, test_id: %s" % test_id)
        current_app.logger.error("get_upload_url ERROR: No Tests!, test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    # get question
    user_id = session.get("user_id")
    # 这里不能用session存储题号，由于是异步处理，因此session记录到下一题的时候上一题可能还没处理完
    # print("[INFO] get_upload_url: question_num: " + str(question_num) + ", user_name: " +
    #       request.session.get("user_name", "NO USER"))
    current_app.logger.info("get_upload_url: question_num: %s, user_name: %s" % (
        str(question_num), session.get("user_name", "NO USER")))
    question = current_test.questions[str(question_num)]

    """generate file path
    upload file path: 相对目录(audio)/日期/用户id/时间戳+后缀(.wav)
    temp path for copy: 相对目录(temp_audio)/用户id/文件名(同上)
    """

    # 如果数据库没有该题的url，创建url，存数据库 ，然后返回
    # 如果数据库里已经有这题的url，说明是重复请求，不用再创建
    if not question.wav_upload_url:
        file_dir = '/'.join((PathConfig.audio_save_basedir, get_date_str('-'), user_id))
        _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
        file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
        question.wav_upload_url = file_dir + '/' + file_name
        question.file_location = 'BOS'
        current_test.save()
        current_app.logger.info("get_upload_url:newly assigned: %s" % question.wav_upload_url)

    context = {"fileLocation": "BOS", "url": question.wav_upload_url}
    current_app.logger.info("get_upload_url: url: " + question.wav_upload_url)
    return jsonify(errors.success(context))


@exam.route('/upload-success', methods=['POST'])
def upload_success():
    if not current_user.is_authenticated:  # todo: 进一步检查是否有做题权限
        return jsonify(errors.Authorize_needed)
    q_num = request.form.get("nowQuestionNum")
    current_app.logger.info("upload_success: now_question_num: %s, user_name: %s" %
                            (str(q_num), session.get("user_name", "NO USER")))

    test_id = session.get("test_id")  # for production
    # test_id = request.form.get("test_id")  # just for unittest

    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("upload_success: CRITICAL: Test Not Exists!! - test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    # print(current_test.id)  # the model has no field '_id', use .id instead
    questions = current_test['questions']
    # print(questions)

    upload_url = questions[q_num]['wav_upload_url']
    # print("[INFO] upload_success: upload_url: " + upload_url)
    current_app.logger.info("upload_success: upload_url: " + upload_url)

    # change question status to handling
    q = current_test.questions[q_num]
    q.status = 'handling'
    q['analysis_start_time'] = datetime.datetime.utcnow()
    current_test.save()
    time.sleep(1)
    try:
        if q.q_type == 3 or q.q_type == '3':
            ret = analysis_main_3.apply_async(args=(str(current_test.id), str(q_num)), queue='q_type3', priority=10)
            # todo: store ret.id in redis for status query
        else:
            ret = analysis_main_12.apply_async(args=(str(current_test.id), str(q_num)), queue='q_type12', priority=2)
            # todo: store ret.id in redis for status query
        current_app.logger.info("AsyncResult id: %s" % ret.id)
    except Exception as e:
        current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
        return jsonify(errors.exception({'Exception': str(e)}))
    resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": current_test.id.__str__(), "taskID": ret.id}
    return jsonify(errors.success(resp))


@exam.route('/get-result', methods=['POST'])
def get_result():
    time.sleep(10)
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)
    current_app.logger.info("get_result: user_name: " + session.get("user_name", "NO USER"))
    current_test_id = session.get("test_id", DefaultValue.test_id)
    test = CurrentTestModel.objects(id=current_test_id).first()
    if test is None:
        test = HistoryTestModel.objects(current_id=current_test_id).first()
        if test is None:
            current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % current_test_id)
            return jsonify(errors.Exam_not_exist)
    questions = test['questions']
    score = {}
    has_handling = False
    for i in range(ExamConfig.total_question_num, 0, -1):
        current_app.logger.info(questions[str(i)]['status'])
        if questions[str(i)]['status'] == 'finished':
            score[i] = questions[str(i)]['score']
            current_app.logger.info("score" + str(score[i]))
        elif questions[str(i)]['status'] not in ['none', 'url_fetched', 'handling']:
            # return jsonify(errors.Process_audio_failed) 记0分
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
            current_app.logger.info("！！记0分 score" + str(score[i]))
        else:
            has_handling = has_handling | (questions[str(i)]['status'] == 'handling')
            current_app.logger.info(str(i))
            break
    # 判断该测试是否超时
    in_process = ((datetime.datetime.utcnow() - test["test_start_time"]).total_seconds() <
                  ExamConfig.exam_total_time)
    current_app.logger.info("in_process: %s" % str(in_process))
    # 如果回答完问题或超时但已处理完，则计算得分，否则返回正在处理
    if len(score) == len(questions) or (not in_process and not has_handling):
        # final score:
        if not test['score_info']:
            current_app.logger.info("first compute score...")
            test['score_info'] = compute_exam_score(score)
            test.save()
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        else:
            current_app.logger.info("use computed score!")
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        return jsonify(errors.success(result))
    else:
        try_times = session.get("tryTimes", 0) + 1
        session['tryTimes'] = try_times
        # print("try times: " + str(try_times))
        current_app.logger.info("try times: " + str(try_times))
        current_app.logger.info("lenscore: " + str(len(score)) + "lenquestion" + str(len(questions)))
        return jsonify(errors.WIP)


@exam.route('/next-question', methods=['POST'])
def next_question():
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)

    now_q_num = request.form.get("nowQuestionNum")
    current_app.logger.info('nowQuestionNum: %s' % now_q_num)
    # 判断是否有剩余考试次数
    # now_q_num = -1 表示是新的考试
    if now_q_num is None or int(now_q_num) == -1:
        if Setting.LIMIT_EXAM_TIMES and current_user.remaining_exam_num <= 0:
            return jsonify(errors.No_exam_times)
        elif Setting.LIMIT_EXAM_TIMES and current_user.remaining_exam_num > 0:
            current_user.remaining_exam_num -= 1
            current_user.save()
        now_q_num = 0
        # 生成当前题目
        current_app.logger.info('init exam...')
        test_id = init_question(session["user_id"])
        if not test_id:
            return jsonify(errors.Init_exam_failed)
        else:
            session["test_id"] = test_id
        session["init_done"] = True
        session["new_test"] = False
    # 获得下一题号 此时now_q_num最小是0
    next_question_num = int(now_q_num) + 1
    session["question_num"] = next_question_num
    current_app.logger.info("api next-question: username: %s, next_question_num: %s" % (
        current_user.name, next_question_num))
    # 如果超出最大题号，如用户多次刷新界面，则重定向到结果页面
    if next_question_num > ExamConfig.total_question_num:
        session["question_num"] = 0
        session["new_test"] = True
        return jsonify(errors.Exam_finished)
    # 根据题号查找题目
    context = question_dealer(next_question_num, session["test_id"], session["user_id"])
    if not context:
        return jsonify(errors.Get_question_failed)
    # 判断考试是否超时，若超时则返回错误
    if context['examLeftTime'] <= 0:
        return jsonify(errors.Test_time_out)

    return jsonify(errors.success(context))


@exam.route('/find-left-exam', methods=['POST'])
def find_left_exam():
    # 判断断电续做功能是否开启
    if ExamConfig.detect_left_exam:
        # 首先判断是否有未做完的考试
        user_id = current_user.id.__str__()
        current_app.logger.info("find_left_exam: user id: %s" % user_id)
        left_exam = CurrentTestModel.objects(user_id=user_id).order_by('-test_start_time').first()
        if not left_exam:
            return jsonify(errors.success({"info": "没有未完成的考试"}))
        in_process = ((datetime.datetime.utcnow() - left_exam["test_start_time"]).total_seconds() <
                      ExamConfig.exam_total_time)
        if in_process:
            # 查找到第一个未做的题目
            for key, value in left_exam['questions'].items():
                status = value['status']
                if status in ['none', 'url_fetched']:
                    return jsonify(errors.info("有未完成的考试", {"next_q_num": key}))
        return jsonify(errors.success({"info": "没有未完成的考试"}))
    else:
        return jsonify(errors.success({"info": "没有未完成的考试"}))


def init_question(user_id):
    current_test = CurrentTestModel()
    user = UserModel.objects(id=user_id).first()
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
        q_current = CurrentQuestionEmbed(q_id=q.id.__str__(), q_type=q.q_type, q_text=q.text, wav_upload_url='')
        current_test.questions.update({str(i + 1): q_current})
        q.update(inc__used_times=1)  # update

    # save
    current_test.save()
    return current_test.id.__str__()


def question_dealer(question_num, test_id, user_id) -> dict:
    # get test
    test = CurrentTestModel.objects(id=test_id).first()
    if test is None:
        current_app.logger.error("question_generator ERROR: No Tests!, test_id: %s" % test_id)
        return {}

    # wrap question
    question = test.questions[str(question_num)]
    context = {"questionType": question.q_type,
               "questionNumber": question_num,
               "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
               "lastQuestion": question_num == ExamConfig.total_question_num,
               "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
               "questionInfo": QuestionConfig.question_type_tip[question.q_type],
               "questionContent": question.q_text,
               "examLeftTime": ExamConfig.exam_total_time - (datetime.datetime.utcnow() - test[
                   'test_start_time']).total_seconds(),
               "examTime": ExamConfig.exam_total_time
               }

    # update and save
    question.status = 'url_fetched'
    test.current_q_num = question_num
    test.save()

    # log question id to user's historical questions
    user = UserModel.objects(id=user_id).first()
    if user is None:
        current_app.logger.error("question_dealer: ERROR: user not find")
    user.questions_history.update({question.q_id: datetime.datetime.utcnow()})
    user.save()

    return context
