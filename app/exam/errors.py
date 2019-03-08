#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7


def success(x=None):
    d = {'code': 0, 'msg': 'success'}
    return {**d, **x}


def error(x=None):
    d = {'code': 1, 'msg': 'error'}
    return {**d, **x}


def exception(x=None):
    d = {'code': 1, 'msg': 'exception'}
    return {**d, **x}


Params_error = {'code': 4000, 'msg': '请求参数错误'}
Exam_not_exist = {'code': 4001, 'msg': '测试不存在'}
Add_task_failed = {'code': 4101, 'msg': '', 'needDisplay': True, 'tip': '添加任务失败'}
