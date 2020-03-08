#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-08

import datetime
from functools import wraps

from app_config import redis_client


def mutex_with_redis(lock_time):
    def inner_deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = 'aps_lock:%s:%s' % (func.__module__, func.__name__)
            val = str(datetime.datetime.utcnow())
            if redis_client.set(key, val, ex=lock_time, nx=True):
                func(*args, **kwargs)

        return wrapper

    return inner_deco
