#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-1-6

from celery import Celery

pw = 'ise_expression'
celery_broker = 'redis://:%s@redis-server.expression.hosts:6379/0' % pw
celery_backend = celery_broker

app = Celery('tasks', broker=celery_broker, backend=celery_backend)


@app.task(name='analysis_12')
def analysis_main_12(current_id_str, q_num_str):
    pass


@app.task(name='analysis_3')
def analysis_main_3(current_id_str, q_num_str):
    pass


@app.task(name='analysis_pretest')
def analysis_wav_pretest(test_id_str):
    pass