# -*- coding: utf-8 -*-
# Time       : 2019/3/18 11:43
# Author     : tangdaye
# Description: admin util

_characters = '1234567890abcdefghijklmnopqrstuvwxyz'


def generate_code(length=4):
    import random
    s = ''
    for i in range(length):
        s += _characters[int(random.random() * 36)]
    return s


# 标准时间戳，秒为单位
def timestamp2datetime(stamp):
    import datetime
    return datetime.datetime.utcfromtimestamp(stamp)


def str_to_bool(str):
    return True if str.lower() == 'true' else False
