#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-06

from .__analysis_tasks_decl__ import analysis_main_12, analysis_main_3, analysis_wav_pretest
from celery.result import AsyncResult
from flask import current_app


class CeleryQueue(object):
    @staticmethod
    def put_task(q_type, test_id: str, q_num=None):
        """
        创建异步评分任务
        :param q_type: 在(pretest, 1, 2, 3)中选择
        :param test_id: string
        :param q_num: 需分析的题号，pretest时留空，其他情况不可留空
        :return: task_id, exception
        """
        try:
            if q_type == 'pretest':
                ret = analysis_wav_pretest.apply_async(args=(str(test_id),), queue='q_pre_test', priority=20)
            elif q_type in [3, '3']:
                ret = analysis_main_3.apply_async(args=(str(test_id), str(q_num)), queue='q_type3', priority=10)
                # todo: store ret.id in redis for status query
            elif q_type in [1, 2, '1', '2']:
                ret = analysis_main_12.apply_async(args=(str(test_id), str(q_num)), queue='q_type12', priority=2)
                # todo: store ret.id in redis for status query
            else:
                raise Exception('Unknown q_type')
            current_app.logger.info("AsyncResult id: %s" % ret.id)
            return ret.id, None
        except Exception as e:
            return None, e

    @staticmethod
    def is_task_finished(task_id: str):
        task = AsyncResult(task_id)
        return task.ready()
