#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7


def success(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 0, 'msg': 'success'}
    if x:
        return {**d, **x}
    else:
        return d


def error(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 1, 'msg': 'error'}
    if x:
        return {**d, **x}
    else:
        return d


def exception(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 1, 'msg': 'exception'}
    if x:
        return {**d, **x}
    else:
        return d


def redirect(next_url):
    """
    :type next_url: str
    :return: dict
    """
    d = {'code': 3, 'msg': 'redirect'}
    if next_url:
        return {**d, **{'next': next_url}}
    else:
        return d


# todo: 确定错误码，及是否需要needDisplay字段
Params_error = {'code': 4000, 'msg': '请求参数错误'}
Exam_not_exist = {'code': 4001, 'msg': '测试不存在'}
Add_task_failed = {'code': 4101, 'msg': '', 'needDisplay': True, 'tip': '添加任务失败'}

Authorize_needed = {'code': 4300, 'msg': '需要登录', 'needDisplay': True}
Authorize_failed = {'code': 4301, 'msg': '账号或密码错误', 'needDisplay': True}
User_not_exist = {'code': 4302, 'msg': '用户不存在', 'needDisplay': True}
User_already_exist = {'code': 4303, 'msg': '用户已存在', 'needDisplay': True}
Already_logged_in = {'code': 4304, 'msg': '用户已经登录', 'needDisplay': True}
Register_not_allowed = {'code': 4305, 'msg': '当前不允许注册', 'needDisplay': True}

Init_exam_failed = {'code': 5101, 'msg': '题目生成失败', 'needDisplay': True}
Get_question_failed = {'code': 5102, 'msg': '获取题目失败', 'needDisplay': True}
Process_audio_failed = {'code': 5103, 'msg': '获取题目失败', 'needDisplay': True}
WIP = {'code': 5104, 'msg': '正在处理', "status": 'InProcess', 'needDisplay': True}
