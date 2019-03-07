#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7


def success(x=None):
    d = {'code': 0, 'msg': 'success'}
    return {**d, **x}


Add_task_failed = {'code': 4, 'msg': '', 'needDisplay': True, 'tip': '添加任务失败'}
