#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-08

import datetime
from app_config import redis_client


def get_a_redis_lock(func, seconds=600):
    key = 'aps_lock:%s:%s' % (func.__module__, func.__name__)
    val = str(datetime.datetime.utcnow())
    return redis_client.set(key, val, ex=seconds, nx=True)
