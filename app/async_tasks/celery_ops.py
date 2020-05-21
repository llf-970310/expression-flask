#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-06

from .celery_config import analysis_main_12, analysis_main_3, analysis_wav_pretest, queues
from celery.result import AsyncResult
from flask import current_app
from app_config import redis_client


class MyCelery(object):
    @staticmethod
    def put_task(q_type, test_id: str, q_num=None, use_lock=True):
        """
        创建异步评分任务
        :param q_type: 在(pretest, 1, 2, 3)中选择
        :param test_id: string
        :param q_num: 需分析的题号，pretest时留空，其他情况不可留空
        :param use_lock: 是否使用redis锁
        :return: task_id, exception
        """
        try:
            if use_lock:
                key = 'celery_lock:%s-%s-%s' % (q_type, test_id, q_num)
                val = ''
                lock = redis_client.set(key, val, ex=60, nx=True)
                if not lock:
                    raise Exception('Failed to get redis lock')
            if q_type == 'pretest':
                ret = analysis_wav_pretest.apply_async(args=(str(test_id),), queue=queues.pretest, priority=20)
            elif q_type in [3, '3']:
                ret = analysis_main_3.apply_async(args=(str(test_id), str(q_num)), queue=queues.type3, priority=10)
            elif q_type in [1, 2, 5, 6, '1', '2', '5', '6', 7, '7']:
                ret = analysis_main_12.apply_async(args=(str(test_id), str(q_num)), queue=queues.type12, priority=2)
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

    @staticmethod
    def get_queue_length(queue) -> int:
        """
        获取指定队列中积压的任务数
        :param queue: 队列名，使用celery_config中的queues成员指定，如queues.pretest
        :return: 队列长度
        """
        return redis_client.llen(queue)

    @classmethod
    def get_all_queue_length(cls) -> int:
        n = 0
        for q in queues:
            n += cls.get_queue_length(q)
        return n
