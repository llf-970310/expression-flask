#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25
import random
import traceback
import Levenshtein

from flask import request, current_app, jsonify
from flask_login import current_user, login_required

from app import errors
from app.exam.utils import *
from app.models.exam import *
from app.async_tasks import MyCelery
from . import exam
from .exam_config import PathConfig, ExamConfig, QuestionConfig, DefaultValue, Setting
from .utils import QuestionUtils

# todo: 保存put_task接口返回的ret.id到redis，于查询考试结果时查验，减少读库次数

# TODO: pretest完全使用任务队列完成，不使用数据库
# TODO: 参照batch_test_views.py更改接口为REST风格

"""
正式评测中考试状态的控制：
1. 使用Redis存放，调用ExamSession.set/get/delete控制；
2. 初始化考试时，设置test_id（数据库current.id）和testing（字符串"True"，因Redis不支持bool类型）；
3. 最后一题上传成功后，清空test_id和testing，同时设置last_test_id，供获取结果时使用；
4. 获取结果时使用last_test_id查询，（原有的test_id已被清除）；
5. 再次考试时检查test_id和testing判断有无未完成考试。
"""


@exam.route('/pretest-wav-info', methods=['GET'])
@login_required
def get_test_wav_info():
    user_id = str(current_user.id)
    wav_test = WavPretestModel()
    wav_test['text'] = QuestionConfig.test_text['content']
    wav_test['user_id'] = user_id
    wav_test.save()
    current_app.logger.info("get_test_wav_info: return data! test id: %s, user name: %s" % (wav_test.id.__str__(),
                                                                                            current_user.name))
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


@exam.route('/pretest-wav-url', methods=['GET'])
@login_required
def get_test_wav_url():
    test_id = request.args.get('testId')
    if not test_id:
        return jsonify(errors.Params_error)
    wav_test = WavPretestModel.objects(id=test_id).first()
    if not wav_test:
        current_app.logger.error("get_test_wav_url: no such test! test id: %s, user name: %s" %
                                 (test_id, current_user.name))
        return jsonify(errors.success(errors.Test_not_exist))
    user_id = str(current_user.id)
    file_dir = '/'.join((PathConfig.audio_test_basedir, get_server_date_str('-'), user_id))
    _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
    file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
    wav_test['wav_upload_url'] = file_dir + '/' + file_name
    wav_test['file_location'] = 'BOS'
    wav_test.save()
    current_app.logger.info("get_test_wav_url: return data! test id: %s, url: %s, user name: %s" %
                            (test_id, wav_test['wav_upload_url'], current_user.name))
    return jsonify(errors.success({
        "fileLocation": "BOS",
        "url": wav_test['wav_upload_url'],
        "test_id": wav_test.id.__str__()
    }))


@exam.route('/pretest-analysis', methods=['POST'])
@login_required
def upload_test_wav_success():
    test_id = request.form.get('testId')
    wav_test = WavPretestModel.objects(id=test_id).first()
    if not wav_test:
        current_app.logger.error("[PretestNotExist][upload_test_wav_success]test id: %s, user name: %s" %
                                 (test_id, current_user.name))
        return jsonify(errors.success(errors.Test_not_exist))
    wav_test.update(set__result__status='handling')
    _, err = MyCelery.put_task('pretest', test_id)
    if err:
        current_app.logger.error('[PutTaskException][upload_test_wav_success]test_id:%s,'
                                 'exception:\n%s' % (test_id, traceback.format_exc()))
        return jsonify(errors.exception({'Exception': str(err)}))
    current_app.logger.info("upload_test_wav_success: return data! test id: %s, user name: %s" %
                            (test_id, current_user.name))
    return jsonify(errors.success())


@exam.route('/pretest-result', methods=['GET'])
@login_required
def get_pretest_result_v2():
    test_id = request.args.get('testId')
    wav_pretest = WavPretestModel.objects(id=test_id).first()
    test_info = 'test_id: %s, user name: %s' % (test_id, current_user.name)
    if wav_pretest is None:
        current_app.logger.error('[Not Found][get_pretest_result]%s' % test_info)
        return jsonify(errors.Test_not_exist)
    status = wav_pretest['result']['status']
    if status == 'handling':
        return jsonify(errors.WIP)
    elif status == 'finished':
        current_app.logger.info('[Success][get_test_result]%s' % test_info)
        rcg_text = wav_pretest['result']['feature']['rcg_text']
        lev_ratio = Levenshtein.ratio(rcg_text, wav_pretest['text'])
        d = {
            "qualityIsOk": lev_ratio >= 0.6,
            "canRcg": True,
            "levRatio": lev_ratio
        }
        return jsonify(errors.success(d))
    else:
        current_app.logger.info('[Bad Quality][get_test_result]%s' % test_info)
        return jsonify(errors.success({"canRcg": False, "qualityIsOk": False}))


@exam.route('/<question_num>/upload-url', methods=['GET'])
@login_required
def get_upload_url_v2(question_num):
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    # get test
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error(
            "[TestNotFound][get_upload_url_v2]username: %s, test_id: %s" % (current_user.name, test_id))
        return jsonify(errors.Exam_not_exist)

    # get question
    user_id = str(current_user.id)
    current_app.logger.debug("[DEBUG][get_upload_url_v2]question_num: %s, user_name: %s"
                             % (question_num, current_user.name))
    try:
        question = current_test.questions[question_num]
    except Exception as e:
        current_app.logger.error("[GetEmbeddedQuestionException][get_upload_url_v2]question_num: "
                                 "%s, user_name: %s. exception:\n%s"
                                 % (question_num, current_user.name, e))
        return jsonify(errors.Get_question_failed)

    # sts = auth.get_sts_from_redis()  # a production to--do

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
        current_app.logger.info("[NewUploadUrl][get_upload_url]user_id:%s, url:%s"
                                % (current_user.id, question.wav_upload_url))
        current_app.logger.info("[INFO][get_upload_url_v2]new url: " + question.wav_upload_url)

    context = {"fileLocation": "BOS", "url": question.wav_upload_url}
    return jsonify(errors.success(context))


@exam.route('/<question_num>/upload-success', methods=['POST'])
@login_required
def upload_success_v2(question_num):
    # get test
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("[TestNotFound][upload_success_v2]test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)
    try:
        question = current_test.questions[question_num]
    except Exception as e:
        current_app.logger.error("[GetEmbeddedQuestionException][get_upload_url_v2]question_num: "
                                 "%s, user_name: %s. exception:\n%s"
                                 % (question_num, current_user.name, e))
        return jsonify(errors.Get_question_failed)
    q_type = question['q_type']  # EmbeddedDocument不是dict，没有get方法

    # todo: 任务队列应放更多信息，让评分节点直接取用，避免让评分节点查url
    task_id, err = MyCelery.put_task(q_type, current_test.id, question_num)
    if err:
        current_app.logger.error('[PutTaskException][upload_success]q_type:%s, test_id:%s,'
                                 'exception:\n%s' % (q_type, current_test.id, traceback.format_exc()))
        return jsonify(errors.exception({'Exception': str(err)}))
    current_app.logger.info("[PutTaskSuccess][upload_success]dataID: %s" % str(current_test.id))

    # 最后一题上传完成，去除正在测试状态，设置last_test_id
    if int(question_num) >= ExamConfig.total_question_num:
        try:
            ExamSession.delete(current_user.id, 'testing')
            ExamSession.rename(current_user.id, 'test_id', 'last_test_id')
            ExamSession.expire(current_user.id, 'last_test_id', 3600)
        except Exception as e:
            current_app.logger.error('[ExamSessionRenameError]%s' % e)
            return jsonify(errors.exception({'Exception': str(e)}))

    resp = {
        "status": "Success",
        "desc": "添加任务成功，等待服务器处理",
        "dataID": str(current_test.id),
        "taskID": task_id
    }
    return jsonify(errors.success(resp))


@exam.route('/get-result', methods=['POST'])
@login_required
def get_result():
    # current_app.logger.debug("get_result: user_name: " + current_user.name)
    last_test_id = ExamSession.get(current_user.id, "last_test_id", DefaultValue.test_id)
    if not last_test_id:
        return jsonify(errors.Check_history_results)
    test = CurrentTestModel.objects(id=last_test_id).first()
    if test is None:
        test = HistoryTestModel.objects(current_id=last_test_id).first()
        if test is None:
            current_app.logger.error("upload_file ERROR: No Tests!, test_id: %s" % last_test_id)
            return jsonify(errors.Exam_not_exist)
    questions = test['questions']
    score = {}
    has_handling = False
    for i in range(ExamConfig.total_question_num, 0, -1):
        if questions[str(i)]['status'] == 'finished':
            score[i] = questions[str(i)]['score']
            current_app.logger.info("get_result: status is finished! index: %s, score: %s, test_id: %s, user name: %s"
                                    % (str(i), str(score[i]), last_test_id, current_user.name))
        elif questions[str(i)]['status'] not in ['none', 'question_fetched', 'url_fetched', 'handling']:
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
            current_app.logger.info("get_result: ZERO score! index: %s, score: %s, test_id: %s, user name: %s"
                                    % (str(i), str(score[i]), last_test_id, current_user.name))
        else:
            has_handling = has_handling | (questions[str(i)]['status'] == 'handling')
            current_app.logger.info("get_result: status is handling! index: %s , test_id: %s, user name: %s"
                                    % (str(i), last_test_id, current_user.name))

    # 判断该测试是否超时
    in_process = ((datetime.datetime.utcnow() - test["test_start_time"]).total_seconds() < ExamConfig.exam_total_time)
    current_app.logger.info("get_result: in_process: %s, test_id: %s, user name: %s" %
                            (str(in_process), last_test_id, current_user.name))
    # 如果回答完问题或超时但已处理完，则计算得分，否则返回正在处理
    if (len(score) == len(questions)) or (not in_process and not has_handling):
        # final score:
        if not test['score_info']:
            current_app.logger.info("get_result: first compute score... test_id: %s, user name: %s" %
                                    (last_test_id, current_user.name))
            test['score_info'] = compute_exam_score(score)
            test.save()
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        else:
            current_app.logger.info("get_result: use computed score! test_id: %s, user name: %s" %
                                    (last_test_id, current_user.name))
            result = {"status": "Success", "totalScore": test['score_info']['total'], "data": test['score_info']}
        ExamSession.set(current_user.id, 'tryTimes', 0)
        current_app.logger.info("get_result: return data! test_id: %s, user name: %s, result: %s" %
                                (last_test_id, current_user.name, str(result)))
        return jsonify(errors.success(result))
    else:
        try_times = int(ExamSession.get(current_user.id, "tryTimes", 0)) + 1
        ExamSession.set(current_user.id, 'tryTimes', str(try_times))
        current_app.logger.info("get_result: handling!!! try times: %s, test_id: %s, user name: %s" %
                                (str(try_times), last_test_id, current_user.name))
        return jsonify(errors.WIP)


@exam.route('/next-question', methods=['POST'])
@login_required
def next_question():
    nowQuestionNum = request.form.get("nowQuestionNum")
    current_app.logger.info('next_question: nowQuestionNum: %s, user_name: %s' % (nowQuestionNum, current_user.name))
    # 判断是否有剩余考试次数
    # nowQuestionNum = -1 表示是新的考试
    if (nowQuestionNum is None) or (int(nowQuestionNum) == -1) or (not ExamSession.get(current_user.id, "test_id")):
        if Setting.LIMIT_EXAM_TIMES and current_user.remaining_exam_num <= 0:
            return jsonify(errors.No_exam_times)
        elif Setting.LIMIT_EXAM_TIMES and current_user.remaining_exam_num > 0:
            current_user.remaining_exam_num -= 1
            current_user.save()
        nowQuestionNum = 0
        # 生成当前题目
        current_app.logger.info('init exam...')
        # 调试发现session["user_id"]和current_user.id相同？？(但应使用current_user.id)
        test_id = QuestionUtils.init_question(current_user)
        if not test_id:
            return jsonify(errors.Init_exam_failed)
        ExamSession.set(current_user.id, 'test_id', test_id)
        ExamSession.set(current_user.id, 'testing', 'True')  # for find-left-exam
    # 获得下一题号 此时now_q_num最小是0
    next_question_num = int(nowQuestionNum) + 1
    ExamSession.set(current_user.id, 'question_num', next_question_num)
    current_app.logger.info(
        "next-question: username: %s, next_question_num: %s" % (current_user.name, next_question_num))
    # 如果超出最大题号，如用户多次刷新界面，则重定向到结果页面
    if next_question_num > ExamConfig.total_question_num:
        ExamSession.set(current_user.id, 'question_num', 0)
        return jsonify(errors.Exam_finished)
    # 根据题号查找题目
    the_test_id = ExamSession.get(current_user.id, 'test_id')
    context = QuestionUtils.question_dealer(next_question_num, the_test_id, str(current_user.id))
    if not context:
        return jsonify(errors.Get_question_failed)
    # 判断考试是否超时，若超时则返回错误
    if context['examLeftTime'] <= 0:
        return jsonify(errors.Test_time_out)
    current_app.logger.info("next_question: return data: %s, user name: %s" % (str(context), current_user.name))
    return jsonify(errors.success(context))


@exam.route('/find-left-exam', methods=['POST'])
@login_required
def find_left_exam():
    # 判断断电续做功能是否开启
    if ExamConfig.detect_left_exam:
        # 首先判断是否有未做完的考试
        test_id = ExamSession.get(current_user.id, 'test_id')
        is_testing = ExamSession.get(current_user.id, 'testing')
        if test_id is not None and is_testing == 'True':
            left_exam = CurrentTestModel.objects(id=test_id).first()
            if left_exam:
                # 查找到第一个未做的题目
                for key, value in left_exam['questions'].items():
                    status = value['status']
                    if status in ['none', 'question_fetched', 'url_fetched']:
                        current_app.logger.info("[LeftExamFound][find_left_exam]user name: %s, test_id: %s" %
                                                (current_user.name, left_exam.id))
                        return jsonify(errors.info("有未完成的考试", {"next_q_num": key}))
    current_app.logger.debug("[NoLeftExamFound][find_left_exam]user name: %s" % current_user.name)
    return jsonify(errors.success({"info": "没有未完成的考试"}))
    #     # 首先判断是否有未做完的考试
    #     user_id = current_user.id.__str__()
    #     current_app.logger.info("find_left_exam: user id: %s" % user_id)
    #     left_exam = CurrentTestModel.objects(user_id=user_id).order_by('-test_start_time').first()
    #     if not left_exam:
    #         current_app.logger.info("find_left_exam: no left exam, user name: %s" % current_user.name)
    #         return jsonify(errors.success({"info": "没有未完成的考试"}))
    #     in_process = ((datetime.datetime.utcnow() - left_exam["test_start_time"]).total_seconds() <
    #                   ExamConfig.exam_total_time)
    #     if in_process:
    #         # 查找到第一个未做的题目
    #         for key, value in left_exam['questions'].items():
    #             status = value['status']
    #             if status in ['none', 'question_fetched', 'url_fetched']:
    #                 current_app.logger.info("find_left_exam: HAS left exam, user name: %s, test_id: %s" %
    #                                         (current_user.name, left_exam.id.__str__()))
    #                 return jsonify(errors.info("有未完成的考试", {"next_q_num": key}))
    #     current_app.logger.info("find_left_exam: no left exam, user name: %s" % current_user.name)
    #     return jsonify(errors.success({"info": "没有未完成的考试"}))
    #
    # current_app.logger.debug("[NoLeftExamFound][find_left_exam]user name: %s" % current_user.name)
    # return jsonify(errors.success({"info": "没有未完成的考试"}))


# upload url TEST - 2020-04-23
@exam.route('/<question_num>/upload-url-bt202004', methods=['GET'])
@login_required
def get_upload_url_v2_bt202004(question_num):
    given_url = request.args.get('givenUrl')
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    # get test
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error(
            "[TestNotFound][get_upload_url_v2]username: %s, test_id: %s" % (current_user.name, test_id))
        return jsonify(errors.Exam_not_exist)

    # get question
    user_id = str(current_user.id)
    current_app.logger.debug("[DEBUG][get_upload_url_v2]question_num: %s, user_name: %s"
                             % (question_num, current_user.name))
    try:
        question = current_test.questions[question_num]
    except Exception as e:
        current_app.logger.error("[GetEmbeddedQuestionException][get_upload_url_v2]question_num: "
                                 "%s, user_name: %s. exception:\n%s"
                                 % (question_num, current_user.name, e))
        return jsonify(errors.Get_question_failed)

    # sts = auth.get_sts_from_redis()  # a production to--do

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
        question.wav_upload_url = given_url
        question.file_location = 'BOS'
        question.status = 'url_fetched'
        current_test.save()
        current_app.logger.info("[NewUploadUrl][get_upload_url]user_id:%s, url:%s"
                                % (current_user.id, question.wav_upload_url))
        current_app.logger.info("[INFO][get_upload_url_v2]new url: " + question.wav_upload_url)

    context = {"fileLocation": "BOS", "url": question.wav_upload_url}
    return jsonify(errors.success(context))
