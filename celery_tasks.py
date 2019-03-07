#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-1-6

from celery import Celery
from django.conf import settings

pw = settings.SESSION_REDIS['password']
# celery_broker = 'amqp://ise:ise_expression@expression.iselab.cn:5672//'
celery_broker = 'redis://:%s@expression.iselab.cn:6379/0' % pw
celery_backend = celery_broker

app = Celery('tasks', broker=celery_broker, backend=celery_backend)


@app.task
def analysis_main_12(current_id_str, q_num_str):
    pass


@app.task
def analysis_main_3(current_id_str, q_num_str):
    pass
