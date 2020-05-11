#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2019/12/16
# 微信小程序 christmas2019

import random
import traceback
import time
import datetime

from flask import request, current_app, jsonify

from app import errors, db
from app.exam.utils.misc import get_server_date_str
from app.models.exam import CurrentQuestionEmbed
from app.models.question import QuestionModel
from app.async_tasks import MyCelery
from . import exam
from .exam_config import PathConfig
from app.auth.util import wxlp_get_sessionkey_openid
from app.admin.util import generate_random_code


# Model
class BtCurrentTestModel(db.DynamicDocument):
    """
    bt_current
    """
    user_id = db.StringField(max_length=32, default=None)
    openid = db.StringField(max_length=64, default=None)  # wx_christmas2019活动使用
    test_start_time = db.DateTimeField()
    paper_type = db.ListField()
    current_q_num = db.IntField(min_value=1, default=1)
    score_info = db.DictField(default={})
    questions = db.DictField(default={})
    all_analysed = db.BooleanField()  # 这个考试中的所有回答是否都被分析过
    # make questions a dict rather than a list so as to be able update one question w/o affecting other questions

    meta = {'collection': 'bt_current'}


class WxBtConfig(object):
    """ 小程序账号相关配置 """
    audio_extension = '.m4a'
    # appid = 'wx23f0c43d3ca9ed9d'  # tangdaye
    # secret = '3d791d2ef69556abb746da30df4aa8e6'
    appid = 'wxdd39ae16bc3a45e3'  # parclab
    secret = 'b7efb9c654b8050eb9af7a13e33dace5'
    wx_user_id = '5e00c1baa8c688039232e2e3'  # wxbt_christmas2019@site.com
    xuanzeti_index = 10001
    q8_index = 10002
    q9_index = 10003


def wxbt_gen_upload_url(openid, q_unm):
    openid = str(openid)

    """generate file path
    upload file path: 相对目录(audio)/日期/用户id/时间戳+后缀
    temp path for copy: 相对目录(temp_audio)/用户id/文件名(同上)
    """

    file_dir = '/'.join((PathConfig.audio_save_basedir, '0-bt-christmas2019', get_server_date_str('-'), openid))
    _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
    file_name = "%s-%s%s" % (q_unm, _temp_str, WxBtConfig.audio_extension)
    wav_upload_url = file_dir + '/' + file_name
    return wav_upload_url


@exam.route('/wxbt/upload-success', methods=['POST'])
def wxbt_upload_success():
    """
    请求参数：questionNum, testID （json）
    上传音频完成，告知后端可以进行处理
    """
    q_num = str(request.json.get("questionNum"))
    test_id = str(request.json.get("testID"))
    if q_num is None or test_id is None:
        return jsonify(errors.Params_error)
    current_app.logger.info("wx:upload_success:question_num: %s, current_id: %s" % (str(q_num), test_id))

    current_test = BtCurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("upload_success: ERROR: Test Not Exists!! - test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    q = current_test.questions.get(q_num)
    if q is None:
        return jsonify(errors.error({'msg': '题号无效'}))
    upload_url = q['wav_upload_url']
    current_app.logger.info("upload_success: upload_url: " + upload_url)

    # change question status to handling
    q.status = 'handling'
    q['analysis_start_time'] = datetime.datetime.utcnow()
    current_test.save()

    task_id, err = MyCelery.put_task(q.q_type, current_test.id, q_num, use_lock=False)
    if err:
        current_app.logger.error('[PutTaskException][wxbt_upload_success]q_type:%s, test_id:%s,'
                                 'exception:\n%s' % (q.q_type, current_test.id, traceback.format_exc()))
        return jsonify(errors.exception({'Exception': str(err)}))
    current_app.logger.info("[PutTaskSuccess][wxbt_upload_success]dataID: %s" % str(current_test.id))
    resp = {
        "status": "Success",
        "desc": "添加任务成功，等待服务器处理",
        "dataID": str(current_test.id),
        "taskID": task_id
    }
    return jsonify(errors.success(resp))


@exam.route('/wxbt/questions', methods=['GET'])
def wxbt_get_questions():
    """
    请求参数： nickname, code
    无session,需要返回testID(current记录的id)给前端,之后前端带此testID请求(wx/upload-success)
    """
    nickname = request.args.get("nickname")
    code = request.args.get("code")
    if nickname in ['', None] or code in ['', None]:
        return jsonify(errors.Params_error)
    current_app.logger.info('wxbt_get_questions: nickname: %s, code: %s, ' % (nickname, code))
    # 使用 code 获取用户的 openid
    err_code, _, openid = wxlp_get_sessionkey_openid(code, appid=WxBtConfig.appid, secret=WxBtConfig.secret)
    err_code, _, openid = 0, 'xxx', generate_random_code(length=24)  # overwrite
    # err_code, openid = 0, 'xxx'
    if err_code:
        d = {'err_code': err_code, 'msg': '获取openid出错'}
        return jsonify(errors.error(d))
    current_app.logger.info('wxbt_get_questions: openid: %s, nickname: %s' % (openid, nickname))

    the_exam = BtCurrentTestModel.objects(openid=openid).first()  # 因为可能是重复请求
    if the_exam is None or the_exam.questions['9'].status in ['handling', 'finished', 'error']:
        # 创建新的current记录(新的考试)
        current_app.logger.info('wxbt_get_questions: init exam...')
        the_exam = wxbt_init_question(openid)
        if not the_exam:
            return jsonify(errors.Init_exam_failed)
    # 按格式包装题目并返回
    context = question_dealer(the_exam)
    return jsonify(errors.success(context))


@exam.route('/wxbt/get-result', methods=['GET'])
def wxbt_get_result():
    """
    请求参数： questionNums(list), testID(str) （json格式）
    获取指定current记录的音频题打分
    """
    questions_nums = [str(s) for s in request.json.get("questionNums")]
    test_id = str(request.json.get("testID"))
    if test_id is None:
        return jsonify(errors.Params_error)
    current_app.logger.info("wxbt:get_result:current_id: %s" % test_id)

    current_test = BtCurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("upload_success: ERROR: Test Not Exists!! - test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)

    ret = {'questions': {}}
    for q_num in questions_nums:
        try:
            q = current_test.questions.get(q_num)
            status = q.get("status")
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errors.error({'msg': '题号无效: %s' % q_num}))
        ret['scores'].update({'q_num': {'status': status, 'scores': q.score}})
    return jsonify(errors.success(ret))


def wxbt_init_question(openid: str):
    """
    生成一个current记录, 返回current对象本身
    所有current记录到同一个用户上（wx_christmas2019@site.com, user_id: 5dfa0c005e3dd462f4755877）
     另外创建字段记录其openid
    """
    current_test = BtCurrentTestModel()
    current_test.user_id = WxBtConfig.wx_user_id
    current_test.openid = openid
    current_test.test_start_time = datetime.datetime.utcnow()

    current_test.questions = {}
    xuanzeti = QuestionModel.objects(index=WxBtConfig.xuanzeti_index).first()
    i = 1
    for t in xuanzeti.questions:
        tmp = {
            "type": 4,
            "content": t['text'],
            "options": [{"key": a, "value": b} for a, b in t['options'].items()],
            "index": i
        }
        current_test.questions.update({str(i): tmp})
        i += 1
    q1 = QuestionModel.objects(index=WxBtConfig.q8_index).first()
    q2 = QuestionModel.objects(index=WxBtConfig.q9_index).first()

    q = q1
    _upload_url = wxbt_gen_upload_url(openid, i)
    _upload_url = 'audio/0-bt-christmas2019/8.m4a'
    q_current = CurrentQuestionEmbed(q_id=str(q.id), q_type=q.q_type, q_text=q.text,
                                     wav_upload_url=_upload_url,
                                     file_location='BOS',
                                     status='url_fetched')
    current_test.questions.update({str(i): q_current})
    q.update(inc__used_times=1)  # update
    i += 1

    q = q2
    _upload_url = wxbt_gen_upload_url(openid, i)
    _upload_url = 'audio/0-bt-christmas2019/9.m4a'
    q_current = CurrentQuestionEmbed(q_id=str(q.id), q_type=q.q_type, q_text=q.text,
                                     wav_upload_url=_upload_url,
                                     file_location='BOS',
                                     status='url_fetched')
    current_test.questions.update({str(i): q_current})
    q.update(inc__used_times=1)  # update
    i += 1

    # save
    current_test.save()
    return current_test


def question_dealer(the_exam) -> dict:  # 包装题目,将current记录对象转为前端需要格式
    ret = {
        'testID': str(the_exam.id),
        'questions': []
    }
    for i, n in enumerate(the_exam.questions):
        q = the_exam.questions[n]
        if i < 7:  # 前7题是选择题，已经包装好存在current里
            ret['questions'].append(q)
        else:
            tmp = {'type': q.q_type,
                   'content': q.q_text,
                   'path': q.wav_upload_url,
                   'index': i + 1}
            ret['questions'].append(tmp)
    return ret
