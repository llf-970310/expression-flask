#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-11
import os
import random
import time

from . import exam
from app import errors
from app.models.exam import *
from app.async_tasks import CeleryQueue
import datetime
import traceback
from .exam_config import PathConfig, ExamConfig, DefaultValue, Setting
from flask import request, current_app, jsonify

from .utils import get_server_date_str, compute_exam_score, ExamSession
from .views import init_question, question_dealer

# from flask_login import current_user
from ..models.user import UserModel
current_user = UserModel.objects(id='5c939bb4cb08361b85b63be9').first()
batch_test_id = '5e73670e90d0d5dfb9b4ca38'  # temporary data, only for today's batch test

# logger 内容中的 BT 意为batch test


def find_left_exam(user_id):
    """
    :param user_id: 用户id
    :return: bool: 是否有未完成考试
    :return: current_q_num: 未完成考试id
    """
    # 判断断电续做功能是否开启
    if not ExamConfig.detect_left_exam:
        current_app.logger.debug("find_left_exam: function not enabled. user_id: %s" % user_id)
        return False, None
    if ExamConfig.detect_left_exam:
        test_id = ExamSession.get(user_id, name="test_id")
        # 首先判断是否有未做完的考试
        current_app.logger.debug("find_left_exam for user_id: %s" % user_id)
        if not test_id:
            current_app.logger.debug("find_left_exam: no left exam, user_id: %s" % user_id)
            return False, None
        left_exam = CurrentTestModel.objects(id=test_id).first()
        if not left_exam:
            current_app.logger.error("[BT-ExamNotFound][find_left_exam]exam recorded but not found,"
                                     "user[id]: %s" % user_id)
            return False, None
        else:
            in_process = ((datetime.datetime.utcnow() - left_exam["test_start_time"]).total_seconds() <
                          ExamConfig.exam_total_time)
            if not in_process:
                current_app.logger.debug("find_left_exam: exam expired, user_id: %s" % user_id)
                return False, None
            else:
                # 查找到第一个未做的题目
                questions = left_exam.questions
                for key, value in questions.items():
                    status = value['status']
                    if status in ['none', 'question_fetched', 'url_fetched']:
                        current_app.logger.info("[BT-LeftExamFound][find_left_exam]user_id: %s, test_id: %s" %
                                                (user_id, left_exam.id))
                        # return True, int(key) - 1  # for production
                        return False, None  # only for batch test


# @exam.route('/', methods=['POST'])  # should use this for production (POST /api/exam/)
@exam.route('/bt0319/init-exam', methods=['POST'])
def init_exam_bt():
    force_create = request.args.get('forceCreate', False)
    current_user = UserModel.objects(id='5c939bb4cb08361b85b63be9').first()  # 需要手动重读用户信息， only for batch test
    has_left_exam, now_question_num = find_left_exam(current_user.id)
    if not has_left_exam or force_create:
        # 判断是否有剩余考试次数
        if Setting.LIMIT_EXAM_TIMES and current_user.remaining_exam_num <= 0:
            return jsonify(errors.No_exam_times)
        now_question_num = 0
        # 生成当前题目
        current_app.logger.info('init exam...')
        test_id = init_question(str(current_user.id))
        if not test_id:
            return jsonify(errors.Init_exam_failed)
        else:
            if Setting.LIMIT_EXAM_TIMES:
                current_user.remaining_exam_num -= 1
                current_user.save()
            ExamSession.set(current_user.id, 'test_id', test_id)
    return jsonify(errors.success({'nowQuestionNum': now_question_num}))


@exam.route('/bt0319/next-question', methods=['GET'])
def next_question_bt():
    """
    需携带参数nowQuestionNum，0表示初始化测试后首次获取下一题
    :return:
    """
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    test_id = batch_test_id  # temporary data, only for today's batch test
    now_question_num = request.args.get("nowQuestionNum")
    try:
        next_question_num = int(now_question_num) + 1
        if next_question_num <= 0:  # db中题号从1开始
            raise Exception('Bad request')
    except Exception as e:
        current_app.logger.error('[BT-ParamsError][next_question]nowQuestionNum: %s, user_name: %s'
                                 % (now_question_num, current_user.name))
        return jsonify(errors.Params_error)

    current_app.logger.debug("next-question: username: %s, next_question_num: %s"
                             % (current_user.name, next_question_num))
    # 如果超出最大题号，如用户多次刷新界面，则重定向到结果页面
    if next_question_num > ExamConfig.total_question_num:
        ExamSession.set(current_user.id, 'question_num', 0)
        return jsonify(errors.Exam_finished)
    # production to--do: nowQuestionNum: 限制只能获取当前题目
    ExamSession.set(current_user.id, 'question_num', next_question_num)

    # 根据题号查找题目
    context = question_dealer(next_question_num, test_id, str(current_user.id))
    if not context:
        return jsonify(errors.Get_question_failed)
    # 判断考试是否超时，若超时则返回错误
    if context['examLeftTime'] <= 0:
        return jsonify(errors.Test_time_out)
    current_app.logger.debug("next_question: return data: %s, user name: %s"
                             % (str(context), current_user.name))
    return jsonify(errors.success(context))


@exam.route('/bt0319/<question_num>/upload-url', methods=['GET'])
def get_upload_url_bt(question_num):
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    test_id = batch_test_id  # temporary data, only for today's batch test

    # get test
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("[BT-TestNotFound][get_upload_url]test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    # get question
    user_id = str(current_user.id)
    current_app.logger.debug("[BT-DEBUG][get_upload_url]question_num: %s, user_name: %s"
                             % (str(question_num), current_user.name))
    question = current_test.questions[str(question_num)]

    # sts = auth.get_sts_from_redis()  # a production to--do
    _ = ExamSession.get(user_id, "sts", DefaultValue.test_id)  # just to waste some time, only for batch test

    """generate file path
    upload file path: 相对目录(audio)/日期/用户id/时间戳+后缀(.wav)
    temp path for copy: 相对目录(temp_audio)/用户id/文件名(同上)
    """

    # 如果数据库没有该题的url，创建url，存数据库 ，然后返回
    # 如果数据库里已经有这题的url，说明是重复请求，不用再创建
    if not question.wav_upload_url:
        file_dir = '/'.join((PathConfig.audio_save_basedir, get_server_date_str('-'), user_id))
        _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
        file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
        question.wav_upload_url = file_dir + '/' + file_name
        question.file_location = 'BOS'
        question.status = 'url_fetched'
        current_test.save()
        current_app.logger.info("[BT-NewUploadUrl][get_upload_url]user_id:%s, url:%s"
                                % (current_user.id, question.wav_upload_url))

    # ----------- waste some time, only for batch test:
    file_dir = '/'.join((PathConfig.audio_save_basedir, get_server_date_str('-'), user_id))
    _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
    file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
    question.wav_upload_url = file_dir + '/' + file_name
    question.file_location = 'BOS'
    question.status = 'url_fetched'
    question = current_test.questions[str(question_num)]
    if os.path.exists('/abc/abc'):
        pass
    # -----------------------------

    context = {"fileLocation": "BOS", "url": question.wav_upload_url}
    current_app.logger.info("[BT-INFO][get_upload_url]url: " + question.wav_upload_url)  # for production
    if os.path.exists('/abc/abc'):  # waste some more time, only for batch test
        pass
    return jsonify(errors.success(context))


@exam.route('/bt0319/<question_num>/upload-success', methods=['POST'])
def upload_success_bt(question_num):
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    test_id = batch_test_id  # temporary data, only for today's batch test

    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        # current_app.logger.error("get_upload_url ERROR: No Tests!, test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    question = current_test.questions.get(question_num)  # production to_do: 任务队列应放更多信息，避免让评分节点查url
    q_type = question['q_type']  # EmbeddedDocument不是dict，没有get方法

    # task_id, err = CeleryQueue.put_task(q_type, current_test.id, question_num)  # for production
    task_id, err = CeleryQueue.put_task('2', current_test.id, question_num, use_lock=False)  # batch test

    if err:
        current_app.logger.error('[BT-PutTaskException][upload_success]q_type:%s, test_id:%s,'
                                 'exception:\n%s' % ('2', current_test.id, traceback.format_exc()))
        return jsonify(errors.exception({'Exception': str(err)}))
    current_app.logger.info("[BT-PutTaskSuccess][upload_success_for_test]dataID: %s" % str(current_test.id))
    resp = {
        "status": "Success",
        "desc": "添加任务成功，等待服务器处理",
        "dataID": str(current_test.id),
        "taskID": task_id
    }
    return jsonify(errors.success(resp))


@exam.route('/bt0319/result', methods=['GET'])
def get_result_bt():
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    test_id = batch_test_id  # temporary data, only for today's batch test

    current_app.logger.debug("get_result: user_name: " + current_user.name)
    test = CurrentTestModel.objects(id=test_id).first()
    if test is None:
        test = HistoryTestModel.objects(current_id=test_id).first()
        if test is None:
            current_app.logger.error("[BT-TestNotFound][get_result]test_id: %s" % test_id)
            return jsonify(errors.Exam_not_exist)

    questions = test['questions']
    score = {}
    has_handling = False
    for i in range(ExamConfig.total_question_num, 0, -1):
        if questions[str(i)]['status'] == 'finished':
            score[i] = questions[str(i)]['score']
            current_app.logger.info("get_result: status is finished! index: %s, score: %s, test_id: %s, user name: %s"
                                    % (str(i), str(score[i]), test_id, current_user.name))
        elif questions[str(i)]['status'] not in ['none', 'question_fetched', 'url_fetched', 'handling']:
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
            current_app.logger.info("get_result: ZERO score! index: %s, score: %s, test_id: %s, user name: %s"
                                    % (str(i), str(score[i]), test_id, current_user.name))
        else:
            has_handling = has_handling | (questions[str(i)]['status'] == 'handling')
            current_app.logger.info("get_result: status is handling! index: %s , test_id: %s, user name: %s"
                                    % (str(i), test_id, current_user.name))

    # 判断该测试是否超时
    in_process = ((datetime.datetime.utcnow() - test["test_start_time"]).total_seconds() < ExamConfig.exam_total_time)
    current_app.logger.info("get_result: in_process: %s, test_id: %s, user name: %s" %
                            (str(in_process), test_id, current_user.name))
    # 如果回答完问题或超时但已处理完，则计算得分，否则返回正在处理
    if (len(score) == len(questions)) or (not in_process and not has_handling):
        # final score:
        if not test['score_info']:
            current_app.logger.info("get_result: first compute score... test_id: %s, user name: %s" %
                                    (test_id, current_user.name))
            test['score_info'] = compute_exam_score(score)
            test.save()
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        else:
            current_app.logger.info("get_result: use computed score! test_id: %s, user name: %s" %
                                    (test_id, current_user.name))
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        ExamSession.set(current_user.id, 'tryTimes', 0)
        current_app.logger.info("get_result: return data! test_id: %s, user name: %s, result: %s" %
                                (test_id, current_user.name, str(result)))
        return jsonify(errors.success(result))
    else:
        try_times = ExamSession.get(current_user.id, "tryTimes", 0) + 1
        ExamSession.set(current_user.id, 'tryTimes', try_times)
        current_app.logger.info("get_result: handling!!! try times: %s, test_id: %s, user name: %s" %
                                (str(try_times), test_id, current_user.name))
        return jsonify(errors.WIP)


@exam.route('/upload-success-for-test', methods=['POST'])
def upload_success_for_test():
    upload_url = request.form.get("uploadUrl")
    q_type = request.form.get("questionType")
    if not upload_url or not q_type:
        return jsonify(errors.Params_error)

    current_app.logger.info("upload_success_for_test: upload_url: " + upload_url)

    if q_type == 'pre-test':
        wav_test = WavPretestModel()
        wav_test['result']['status'] = 'handling'
        wav_test.result['analysis_start_time'] = datetime.datetime.utcnow()
        wav_test['wav_upload_url'] = upload_url.lstrip('/expression')
        wav_test['file_location'] = 'BOS'
        wav_test['text'] = '表达力测试将用15分钟的时间，数据化您的表达能力。'
        wav_test.save()

        task_id, err = CeleryQueue.put_task('pretest', wav_test.id, use_lock=False)
        if err:
            current_app.logger.error('[BT-PutTaskException][upload_success_for_test]test_id:%s,'
                                     'exception:\n%s' % (wav_test.id, traceback.format_exc()))
            return jsonify(errors.exception({'Exception': str(err)}))
        resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": str(wav_test.id), "taskID": task_id}
        return jsonify(errors.success(resp))
    else:
        # 新建一个current
        current_test = CurrentTestModel()
        current_test.test_start_time = datetime.datetime.utcnow()
        q = QuestionModel.objects(q_type=int(q_type)).order_by('used_times')[0]
        q_current = CurrentQuestionEmbed(q_dbid=str(q.id), q_type=q.q_type, q_text=q.text, wav_upload_url='')
        current_test.questions = {"1": q_current}
        current_test.save()

        # change question status to handling
        current_test.questions['1'].status = 'handling'
        current_test.questions['1'].wav_upload_url = upload_url.lstrip('/expression')
        current_test.questions['1']['analysis_start_time'] = datetime.datetime.utcnow()
        current_test.questions['1'].file_location = 'BOS'
        current_test.save()

        task_id, err = CeleryQueue.put_task(q.q_type, current_test.id, '1', use_lock=False)
        if err:
            current_app.logger.error('[BT-PutTaskException][upload_success_for_test]q_type:%s, test_id:%s,'
                                     'exception:\n%s' % (q.q_type, current_test.id, traceback.format_exc()))
            return jsonify(errors.exception({'Exception': str(err)}))
        current_app.logger.info("[BT-PutTaskSuccess][upload_success_for_test]dataID: %s" % str(current_test.id))
        resp = {
            "status": "Success",
            "desc": "添加任务成功，等待服务器处理",
            "dataID": str(current_test.id),
            "taskID": task_id
        }
        return jsonify(errors.success(resp))


@exam.route('/get-result-for-test', methods=['POST'])
def get_result_for_test():
    test_id = request.form.get('testID')
    pre_test = request.form.get('preTest')
    if not test_id or (len(test_id) != 12 and len(test_id) != 24):
        return jsonify(errors.Params_error)
    if pre_test is True or pre_test == 'True':
        the_test = WavPretestModel.objects(id=test_id).first()
        if the_test is None:
            return jsonify(errors.Exam_not_exist)
        try:
            result = the_test['result']
            status = result['status']
            start = the_test.test_time
            end = result['analysis_end_time']
            if status != 'error':
                msg = {"status": status, "analysis_start_time": str(start),
                       "analysis_end_time": str(end)}  # 转为str保证时间格式
                return jsonify(errors.success(msg))
            else:
                msg = {"status": status, "stack": result.get('stack'), "analysis_start_time": str(start),
                       "analysis_end_time": str(end)}
            return jsonify(errors.error(msg))
        except Exception as e:
            current_app.logger.error('get_result_for_test: %s' % traceback.format_exc())
            return jsonify(errors.exception({'Exception': str(e)}))
    else:
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
