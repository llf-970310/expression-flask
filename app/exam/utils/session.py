#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-10


from app_config import redis_client
from app.exam.exam_config import DefaultValue


class ExamSession:
    key_format = 'exam-session:%s:%s'

    @classmethod
    def set(cls, user_id, name, value, ex=int(DefaultValue.session_expire), px=None, nx=False, xx=False):
        user_id = str(user_id)
        key = cls.key_format % (user_id, name)
        return redis_client.set(key, value, ex, px, nx, xx)

    @classmethod
    def get(cls, user_id, name, default=None):
        user_id = str(user_id)
        key = cls.key_format % (user_id, name)
        ret = redis_client.get(key)
        return ret.decode() if ret is not None else default

    @classmethod
    def delete(cls, user_id, name):
        user_id = str(user_id)
        key = cls.key_format % (user_id, name)
        return redis_client.delete(key)

    @classmethod
    def rename(cls, user_id, name, new_name):
        user_id = str(user_id)
        key = cls.key_format % (user_id, name)
        new_key = cls.key_format % (user_id, new_name)
        return redis_client.rename(key, new_key)

    @classmethod
    def expire(cls, user_id, name, time):
        user_id = str(user_id)
        key = cls.key_format % (user_id, name)
        return redis_client.expire(key, time)
