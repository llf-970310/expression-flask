#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-11

from . import exam
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify
from celery_tasks import analysis_main_12, analysis_main_3, analysis_wav_test
import datetime
import traceback


@exam.route('/upload-success-for-test', methods=['POST'])
def upload_success_for_test():
    upload_url = request.form.get("uploadUrl")
    q_type = request.form.get("questionType")
    if not upload_url or not q_type:
        return jsonify(errors.Params_error)

    current_app.logger.info("upload_success_for_test: upload_url: " + upload_url)

    if q_type == 'pre-test':
        wav_test = WavTestModel()
        wav_test['result']['status'] = 'handling'
        wav_test['result']['analysis_start_time'] = datetime.datetime.utcnow()
        wav_test['wav_upload_url'] = upload_url.lstrip('/expression')
        wav_test['file_location'] = 'BOS'
        wav_test.save()

        try:
            ret = analysis_wav_test.apply_async(args=[wav_test.id], queue='q_pre_test', priority=20)
            current_app.logger.info("AsyncResult id: %s" % ret.id)
        except Exception as e:
            current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
            return jsonify(errors.exception({'Exception': str(e)}))
        resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": str(wav_test.id), "taskID": ret.id}
        return jsonify(errors.success(resp))
    else:
        # 新建一个current
        current_test = CurrentTestModel()
        current_test.test_start_time = datetime.datetime.utcnow()
        q = QuestionModel.objects(q_type=int(q_type)).order_by('used_times')[0]
        q_current = CurrentQuestionEmbed(q_id=q.id.__str__(), q_type=q.q_type, q_text=q.text, wav_upload_url='')
        current_test.questions = {"1": q_current}
        current_test.save()

        # change question status to handling
        current_test.questions['1'].status = 'handling'
        current_test.questions['1'].wav_upload_url = upload_url.lstrip('/expression')
        current_test.questions['1']['analysis_start_time'] = datetime.datetime.utcnow()
        current_test.questions['1'].file_location = 'BOS'
        current_test.save()

        try:
            if q.q_type == 3 or q.q_type == '3':
                ret = analysis_main_3.apply_async(args=(str(current_test.id), '1'), queue='q_type3', priority=10)
                # todo: store ret.id in redis for status query
            else:
                ret = analysis_main_12.apply_async(args=(str(current_test.id), '1'), queue='q_type12', priority=2)
                # todo: store ret.id in redis for status query
            current_app.logger.info("AsyncResult id: %s" % ret.id)
        except Exception as e:
            current_app.logger.error('upload_success_for_test: celery enqueue:\n%s' % traceback.format_exc())
            return jsonify(errors.exception({'Exception': str(e)}))
        resp = {"status": "Success", "desc": "添加任务成功，等待服务器处理", "dataID": str(current_test.id), "taskID": ret.id}
        return jsonify(errors.success(resp))


@exam.route('/get-result-for-test', methods=['POST'])
def get_result_for_test():
    test_id = request.form.get('testID')
    pre_test = request.form.get('preTest')
    if not test_id or (len(test_id) != 12 and len(test_id) != 24):
        return jsonify(errors.Params_error)
    if pre_test is True or pre_test == 'True':
        the_test = WavTestModel.objects(id=test_id).first()
        if the_test is None:
            return jsonify(errors.Exam_not_exist)
        try:
            result = the_test['result']
            status = result['status']
            start = result['analysis_start_time']
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
