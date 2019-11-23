#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向管理员的accounts相关views,与view无关的具体功能的实现请写在app/accounts/utils.py中,在此尽量只作引用
from flask import request, current_app, jsonify, session
from flask_login import current_user
from app.admin.admin_config import AccountsConfig
from app.admin.util import *
from app.auth.util import admin_login_required
from app.models.invitation import *

from flask import jsonify

from app import errors
from . import admin


@admin.route('/accounts/invite', methods=['POST'])  # url will be .../admin/accounts/test
@admin_login_required
def accounts_invite():
    current_app.logger.info('create invitation request: %s' % request.form.__str__())
    # 检验是否有权限申请邀请码
    form = request.form
    try:
        vip_start_time = timestamp2datetime(float(form.get('vipStartTime').strip()))
        vip_end_time = timestamp2datetime(float(form.get('vipEndTime').strip()))
        remaining_exam_num = int(form.get('remainingExamNum').strip())
        available_times = int(form.get('availableTimes').strip())
        code_num = int(form.get('codeNum').strip())
    except Exception:
        return jsonify(errors.Params_error)
    """
        form 校验规则
        1. vipStartTime必须在vipEndTime之前
        2. vipEndTime必须在现在之后
        3. remainingExamNum要大于0（可用考试次数）
        4. availableTimes要大于0（邀请码可用人数）
        5. codeNum要大于0（邀请码个数）
        6. 各项不为空
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
    if code_num <= 0:
        return jsonify(errors.Params_error)

    invitation_codes = []
    for i in range(0, code_num):
        invitation = InvitationModel()
        invitation.creator = current_user.name
        invitation.activate_users = []
        invitation.vip_start_time = vip_start_time
        invitation.vip_end_time = vip_end_time
        invitation.remaining_exam_num = remaining_exam_num
        invitation.available_times = available_times
        invitation.code = generate_code(AccountsConfig.INVITATION_CODE_LEN)
        invitation.create_time = datetime.datetime.utcnow()
        current_app.logger.info('invitation info:%s' % invitation.__str__())
        # 生成指定位数随机字符串为邀请码
        invitation.save(invitation)
        current_app.logger.info('invitation(id: %s)' % invitation.id)
        invitation_codes.append(invitation.code)
    return jsonify(errors.success({'msg': '生成邀请码成功', 'invitationCode': invitation_codes}))


@admin.route('/accounts/invite', methods=['GET'])
@admin_login_required
def get_invitations():
    invitations = InvitationModel.objects()

    # wrap invitations
    result = []
    for invitation in invitations:
        result.append({
            'code': invitation['code'],
            'creator': invitation['creator'],
            # 邀请码创建时间
            'create_time': convert_datetime_to_str(invitation['create_time']),
            # 邀请码剩余可用次数
            'available_times': invitation['available_times'],
            # 邀请码有效时间
            'vip_start_time': convert_datetime_to_str(invitation['vip_start_time']),
            'vip_end_time': convert_datetime_to_str(invitation['vip_end_time']),
            # 此邀请码支持的测试次数
            'remaining_exam_num': invitation['remaining_exam_num'],
            # 使用此邀请码的用户
            'activate_users': array2str(invitation['activate_users'], 1)
        })
    return jsonify(errors.success({'result': result}))
