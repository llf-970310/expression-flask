#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-28

from app.models.question import QuestionModel
from app_config import redis_client
import pickle


def get_cached_questions(q_type):
    key = 'cached_questions:type_%s' % q_type
    all_qs_bytes = redis_client.get(key)
    if all_qs_bytes:
        return pickle.loads(all_qs_bytes)
    d = {'q_type': q_type, 'index': {'$lte': 10000}}
    questions = QuestionModel.objects(__raw__=d).order_by('used_times')  # 按使用次数倒序获得questions
    cached_qs = []
    for q in questions:
        cached_qs.append(q)
    redis_client.set(key, pickle.dumps(cached_qs), ex=7200, nx=True)
    return cached_qs


def set_cached_questions(q_type, questions):
    key = 'cached_questions:type_%s' % q_type
    redis_client.set(key, pickle.dumps(questions), ex=7200, nx=True)
