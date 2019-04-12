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


def convert_date_to_str(date, separator='') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    return date.strftime("%%Y%s%%m%s%%d" % (separator, separator))


def str_to_bool(str):
    return True if str.lower() == 'true' else False
