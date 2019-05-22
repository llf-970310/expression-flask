#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25
import random

from baidubce.services.bos import bos_client

from app.exam.util import *
from app.models.user import UserModel
from . import exam
from app import errors
from .exam_config import PathConfig, ExamConfig, QuestionConfig, DefaultValue
from app.models.exam import *
from flask import request, current_app, jsonify, session
from flask_login import current_user
from celery_tasks import analysis_main_12, analysis_main_3
import datetime
import traceback
from baidubce.services.bos.bos_client import BosClient

# @exam.route('/upload', methods=['POST'])
# def upload_file():
#     # get question number
#     question_num = request.form.get("nowQuestionNum")
#
#     # # 如果重复上传，直接返回
#     # if request.session.get("start_upload_" + str(question_num), False):
#     #     print("upload_file: REPEAT UPLOAD!!!!!: question_num: " + str(question_num))
#     #     return HttpResponse('{"status":"Success"}', content_type='application/json', charset='utf-8')
#     # # 在session中说明开始上传，防止同一题目重复上传
#     # request.session["start_upload_" + str(question_num)] = True
#
#     # get test
#     test_id = session.get("test_id")
#     test = CurrentTestModel.objects(id=test_id).first()
#     if test is None:
#         # print("[ERROR] upload_file ERROR: No Tests!, test_id: %s" % test_id)
#         current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % test_id)
#         return jsonify(errors.Exam_not_exist)
#
#     # get question
#     question = test.questions[question_num]
#
#     # get file name and dir
#     file_dir = os.path.join(Setting.BASE_DIR, os.path.dirname(question.wav_upload_url))
#     file_name = os.path.basename(question.wav_upload_url)
#
#     video = request.form.get("video")
#     # print("[INFO] upload file start: dir: " + file_dir + ", name: " + file_name)
#     current_app.logger.info("upload file start: dir: " + file_dir + ", name: " + file_name)
#     save_file_to_path(video, file_name, file_dir)
#     # print("[INFO] upload file end: dir: " + file_dir + ", name: " + file_name)
#     current_app.logger.info("upload file end: dir: " + file_dir + ", name: " + file_name)
#     resp = {"status": "Success"}
#     return jsonify(errors.success(resp))


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
            ret = analysis_main_3.apply_async(args=(str(current_test.id), str(q_num)), queue='for_q_type3', priority=10)
            # todo: store ret.id in redis for status query
        else:
            ret = analysis_main_12.apply_async(args=(str(current_test.id), str(q_num)), queue='for_q_type12',
                                               priority=2)
            # todo: store ret.id in redis for status query
        current_app.logger.info("AsyncResult id: %s" % ret.id)
    except Exception as e:
        current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
        return jsonify(errors.exception({'Exception': str(e)}))
    resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": current_test.id.__str__(), "taskID": ret.id}
    return jsonify(errors.success(resp))


@exam.route('/get-result', methods=['POST'])
def get_result():
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)
    current_app.logger.info("get_result: user_name: " + session.get("user_name", "NO USER"))
    current_test_id = session.get("test_id", DefaultValue.test_id)
    test = CurrentTestModel.objects(id=current_test_id).first()
    if test is None:
        current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % current_test_id)
        return jsonify(errors.Exam_not_exist)
    questions = test['questions']

    score = {}
    current_app.logger.info("question_num"+ExamConfig.total_question_num)
    for i in range(6, 0, -1):
        if questions[str(i)]['status'] == 'finished':
            score[i] = questions[str(i)]['score']
            current_app.logger.info("score"+score[i])
        elif questions[str(i)]['status'] != 'none' and questions[str(i)]['status'] != 'url_fetched' and \
                questions[str(i)]['status'] != 'handling':
            return jsonify(errors.Process_audio_failed)
        else:
            break

    if len(score) == len(questions):
        # final score:
        x = {
            "quality": round(score[1]['quality'], 6),
            "main": round(score[2]['main'] * 0.25 + score[3]['main'] * 0.25 + score[4]['main'] * 0.25 + score[5][
                'main'] * 0.25, 6),
            "detail": round(score[2]['detail'] * 0.25 + score[3]['detail'] * 0.25 + score[4]['detail'] * 0.25 +
                            score[5]['detail'] * 0.25, 6),
            "structure": round(score[6]['structure'], 6),
            "logic": round(score[6]['logic'], 6)
        }
        x['total'] = round(x["quality"] * 0.3 + x["main"] * 0.35 + x["detail"] * 0.15
                           + x["structure"] * 0.1 + x["logic"] * 0.1, 6)
        data = {"音质": x['quality'], "结构": x['structure'], "逻辑": x['logic'],
                "细节": x['detail'], "主旨": x['main']}
        result = {"status": "Success", "totalScore": x['total'], "data": data}
        return jsonify(errors.success(result))
    else:
        try_times = session.get("tryTimes", 0) + 1
        session['tryTimes'] = try_times
        # print("try times: " + str(try_times))
        current_app.logger.info("try times: " + str(try_times))
        current_app.logger.info("lenscore: " + str(len(score)) + "lenquestion" +str(len(questions)))
        return jsonify(errors.WIP)


@exam.route('/next-question', methods=['POST'])
def next_question():
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)
    # 关闭浏览器时session过期
    # session.set_expiry(0)
    # init question
    now_q_num = request.form.get("nowQuestionNum")
    current_app.logger.info('nowQuestionNum: %s' % now_q_num)
    if now_q_num is None or now_q_num == '0' or now_q_num == 0:  # TODO: 仅根据前端请求判断不太合理
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
    # 获得下一题号
    next_question_num = int(now_q_num) + 1  # 不能转换时怎么处理,如'aaa'
    session["question_num"] = next_question_num
    current_app.logger.info("api next-question: username: %s, next_question_num: %s" % (
        current_user.name, next_question_num))
    # 如果超出最大题号，如用户多次刷新界面，则重定向到结果页面
    if next_question_num > ExamConfig.total_question_num:
        session["question_num"] = 0
        session["new_test"] = True  # TODO: 这样不合理（重复请求时）,开始做题应单独作为一个接口请求,进行 init exam
        return jsonify(errors.Exam_finished)

    # 根据题号查找题目
    context = question_dealer(next_question_num, session["test_id"], session["user_id"])
    if not context:
        return jsonify(errors.Get_question_failed)
    return jsonify(errors.success(context))


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
               "questionContent": question.q_text
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


@exam.route('/getwav')
def getwav():
    bucket_name='ise-expression-bos'
    object_key='audio/东京爱情故事高潮_铃声之家cnwav.wav'
    file_name='app'
    response = bos_client.list_objects(bucket_name)
    for object in response.contents:
        print(object.key)
    return jsonify(errors.success('chenggong'))
