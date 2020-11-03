#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-06
from celery import Celery

from app.async_tasks import celery_config
from celery.result import AsyncResult
from flask import current_app
from app_config import redis_client

pw = 'ise_expression'
celery_broker = 'amqp://admin:%s@redis-server.expression.hosts:5672/' % pw
celery_backend = 'redis://:%s@redis-server.expression.hosts:6379/7' % pw

app = Celery('tasks', broker=celery_broker, backend=celery_backend)
app.config_from_object(celery_config)


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
                # 此处名称应与 worker 端的 task_name 保持一致
                # 不建议在此指定 queue，在 config 中使用 CELERY_ROUTES 配置
                ret = app.send_task('analysis_pretest', args=(str(test_id),), priority=20)
            elif q_type in [3, '3']:
                ret = app.send_task('analysis_3', args=(str(test_id), str(q_num)), priority=10)
            elif q_type in [1, 2, 5, 6, '1', '2', '5', '6', 7, '7']:
                ret = app.send_task('analysis_12', args=(str(test_id), str(q_num)), priority=2)
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
