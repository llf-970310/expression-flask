#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7


# 应前段要求把x改在data里面
def success(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 0, 'msg': 'success', 'data': {}}
    if x:
        for t in x:
            if t == 'code' or t == 'msg':
                d[t] = x[t]
            else:
                d['data'][t] = x[t]
    return d


def info(msg, x=None):
    d = {'code': 2, 'msg': msg, 'data': {}}
    if x:
        for t in x:
            if t == 'code' or t == 'msg':
                d[t] = x[t]
            else:
                d['data'][t] = x[t]
    return d


def error(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 1, 'msg': 'error', 'data': {}}
    if x:
        for t in x:
            if t == 'code' or t == 'msg':
                d[t] = x[t]
            else:
                d['data'][t] = x[t]
    return d


def exception(x=None):
    """
    :type x: dict or None
    :return: dict
    """
    d = {'code': 1, 'msg': 'exception', 'data': {}}
    if x:
        for t in x:
            if t == 'code' or t == 'msg':
                d[t] = x[t]
            else:
                d['data'][t] = x[t]
    return d


def redirect(next_url):
    """
    :type next_url: str
    :return: dict
    """
    d = {'code': 3, 'msg': 'redirect'}
    if next_url:
        return {**d, **{'data': {'redirect': next_url}}}
    return d


# todo: 确定错误码，及是否需要needDisplay字段
# 请按错误类型聚类，错误码从小到大排序，求求了
Params_error = {'code': 4000, 'msg': '请求参数错误'}
Exam_not_exist = {'code': 4001, 'msg': '测试不存在'}
Add_task_failed = {'code': 4101, 'msg': '添加任务失败'}
Test_not_exist = {'code': 4002, 'msg': '考前测试不存在'}
Test_time_out = {'code': 4003, 'msg': '考试超时'}
No_exam_times = {'code': 4004, 'msg': '没有剩余考试次数'}
Check_history_results = {'code': 4005, 'msg': '请查看历史成绩'}

Question_not_exist = {'code': 4006, 'msg': '题目不存在'}
Optimize_not_exist = {'code': 4007, 'msg': '该题目未进行过优化'}
Vip_expired = {'code': 4008, 'msg': '评测权限已过期'}

Login_required = {'code': 4300, 'msg': '需要登录'}
Authorize_failed = {'code': 4301, 'msg': '账号或密码错误'}
User_not_exist = {'code': 4302, 'msg': '用户不存在'}
User_already_exist = {'code': 4303, 'msg': '用户已存在'}
Already_logged_in = {'code': 4304, 'msg': '用户已经登录'}
Register_not_allowed = {'code': 4305, 'msg': '当前不允许注册'}
Admin_login_required = {'code': 4306, 'msg': '请以管理员身份登录'}
Invitation_code_invalid = {'code': 4307, 'msg': '邀请码无效'}

Student_id_short = {'code': 4037, 'msg': '学号不能少于6位，不足6位请在前面加0补足！'}
Student_id_space = {'code': 4038, 'msg': '学号中间不能有空格！'}
Illegal_invitation_code = {'code': 4039, 'msg': '无效的邀请码'}
Wechat_already_bind = {'code': 4040, 'msg': '该账号已绑定微信，若需重新绑定，请先解绑原微信号'}
Wechat_not_bind={'code':4041,'msg':'未绑定微信，不需要解绑'}
No_history={'code':4042,'msg':'用户暂无历史成绩'}

Score_no_data = {'code': 4701, 'msg': '暂无数据'}
Origin_question_no_more = {'code': 4702, 'msg': '题库中暂无题目'}
Score_criteria_not_exist = {'code': 4703, 'msg': '成绩管理要搜索的条件不存在'}

Exam_finished = {'code': 5100, 'msg': '测试已完成'}
Init_exam_failed = {'code': 5101, 'msg': '题目生成失败'}
Get_question_failed = {'code': 5102, 'msg': '获取题目失败'}
Process_audio_failed = {'code': 5103, 'msg': '获取题目失败'}
Audio_process_failed = {'code': 5105, 'msg': '音频处理出错'}
WIP = {'code': 5104, 'msg': '正在处理'}
