#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向管理员的accounts相关views,与view无关的具体功能的实现请写在app/accounts/utils.py中,在此尽量只作引用
from flask import request, current_app, jsonify, session
from flask_login import current_user
from app.admin.config import AccountsConfig
from app.admin.util import *
from app.models.invitation import *

from flask import jsonify

from app import errors
from . import admin


@admin.route('/accounts/invite', methods=['POST'])  # url will be .../admin/accounts/test
def accounts_invite():
    current_app.logger.info('create invitation request: %s' % request.form.__str__())
    # 检验是否有权限申请邀请码
    if not current_user.is_authenticated:
        return jsonify(errors.Authorize_needed)
    if not current_user.role == 'admin':
        return jsonify(errors.Admin_status_login)
    form, invitation = request.form, InvitationModel()
    try:
        vip_start_time = timestamp2datetime(int(form.get('vipStartTime').strip()))
        vip_end_time = timestamp2datetime(int(form.get('vipEndTime').strip()))
        remaining_exam_num = int(form.get('remainingExamNum').strip())
        available_times = int(form.get('availableTimes').strip())
    except Exception:
        return jsonify(errors.Params_error)
    """
        form 校验规则
        1. vipStartTime必须在vipEndTime之前
        2. vipEndTime必须在现在之后
        3. remainingExamNum要大于0（可用考试次数）
        4. availableTimes要大于0（邀请码可用人数）
        5. 各项不为空
    """
    if not vip_start_time and not vip_end_time and not remaining_exam_num and not available_times:
        return jsonify(errors.Params_error)
    if vip_start_time >= vip_end_time:  # rule 1
        return jsonify(errors.Params_error)
    if vip_end_time <= datetime.datetime.utcnow():  # rule 2
        return jsonify(errors.Params_error)
    if remaining_exam_num <= 0:  # rule 3
        return jsonify(errors.Params_error)
    if available_times <= 0:  # rule 4
        return jsonify(errors.Params_error)

    invitation.creator = current_user.name
    invitation.activate_users = []
    invitation.vip_start_time = vip_start_time
    invitation.vip_end_time = vip_end_time
    invitation.remaining_exam_num = remaining_exam_num
    invitation.available_times = available_times
    invitation.code = generate_code(AccountsConfig.invitation_code_length)
    current_app.logger.info('invitation info:%s' % invitation.__str__())
    # 生成指定位数随机字符串为邀请码
    invitation.save(invitation)
    current_app.logger.info('invitation(id: %s)' % invitation.id)
    return jsonify(errors.success({'msg': '生成邀请码成功', 'invitationCode': invitation.code}))