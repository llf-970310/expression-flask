#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向管理员的accounts相关views,与view无关的具体功能的实现请写在app/accounts/utils.py中,在此尽量只作引用
import json
from flask import request, current_app, jsonify
from flask_login import current_user
from app.admin.admin_config import AccountsConfig
from app.admin.util import *
from app.auth.util import admin_login_required
from app.models.invitation import InvitationModel
from app import errors
from . import admin
import datetime
from app.utils.date_and_time import datetime_fromisoformat  # for py3.6
from app.utils.date_and_time import datetime_to_str


@admin.route('/accounts/invite', methods=['POST'])  # url will be .../admin/accounts/test
@admin_login_required
def accounts_invite():
    """批量创建邀请码

    Form-data Args:
        vipStartTime: 评测权限开始时间
        vipEndTime: 评测权限结束时间
        remainingExamNum: 邀请码包含的评测考试权限
        remainingExerciseNum: 邀请码包含的评测练习权限（暂未使用）
        availableTimes: 邀请码可用人数
        codeNum: 创建邀请码个数

    form 校验规则:
        1. vipStartTime必须在vipEndTime之前
        2. vipEndTime必须在现在之后
        3. remainingExamNum和remainingExerciseNum至少有一个>0（可用考试、练习次数）
        4. availableTimes要大于0（邀请码可用人数）
        5. codeNum要大于0（邀请码个数）
        6. 各项不为空

    Returns:
        jsonify(errors.success({'msg': '生成邀请码成功', 'invitationCode': [...]}))

    """
    current_app.logger.info('create invitation request: %s' % request.form.__str__())
    # 检验是否有权限申请邀请码
    form = request.form
    try:
        vip_start_time = datetime.datetime.utcfromtimestamp(float(form.get('vipStartTime').strip()))
        vip_end_time = datetime.datetime.utcfromtimestamp(float(form.get('vipEndTime').strip()))
        remaining_exam_num = int(form.get('remainingExamNum').strip())
        remaining_exercise_num = int(form.get('remainingExerciseNum').strip())
        available_times = int(form.get('availableTimes').strip())
        code_num = int(form.get('codeNum').strip())
    except Exception as e:
        current_app.logger.error('Params_error:POST admin/accounts/invite: %s' % e)
        return jsonify(errors.Params_error)
    # form 校验
    if not vip_start_time and not vip_end_time and not available_times:
        return jsonify(errors.Params_error)
    if vip_start_time >= vip_end_time:  # rule 1
        return jsonify(errors.Params_error)
    if vip_end_time <= datetime.datetime.utcnow():  # rule 2
        return jsonify(errors.Params_error)
    if not (remaining_exam_num > 0 or remaining_exercise_num > 0):  # rule 3
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
        invitation.remaining_exercise_num = remaining_exercise_num
        invitation.available_times = available_times
        invitation.code = generate_random_code(AccountsConfig.INVITATION_CODE_LEN)
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
    """批量查询邀请码

    Request.args URL Args:
        "currentPage": int,  默认 1
        "pageSize": int,     默认 10
        "conditions": {      可选
            "code": str,
            "createTimeFrom": "2019-11-20 00:00:00",
            "createTimeTo": "2019-11-22 00:00:00",
            "availableTimes": int
        }

    Returns:
        {
          "code": xx,
          "msg": xx,
          "data": {
            "totalCount": int,
            "invitationCodes": [
                {}, {}, {}
            ]
          }
        }
    """
    try:
        conditions = json.loads(request.args.get('conditions'))
        create_time_from = conditions.get('createTimeFrom')
        create_time_to = conditions.get('createTimeTo')
        available_times = conditions.get('availableTimes')
        specify_code = conditions.get('code')
        cp = int(request.args.get('currentPage', 1))
        ps = int(request.args.get('pageSize', 10))
        if cp < 1:
            cp = 1
        if ps < 0:
            ps = 10
        n_from = ps * (cp - 1)
        n_to = n_from + ps
        d = {}
        time_limits = {}
        if create_time_from:
            time_limits.update({'$gte': datetime_fromisoformat(create_time_from)})
        if create_time_to:
            time_limits.update({'$lte': datetime_fromisoformat(create_time_to)})
        if time_limits != {}:
            d.update({'create_time': time_limits})
        if available_times not in [None, '']:
            d.update({'available_times': int(available_times)})
        if specify_code:
            d.update({'code': specify_code})
    except Exception as e:
        current_app.logger.error('Params_error:GET admin/accounts/invite: %s' % e)
        return jsonify(errors.Params_error)
    set_manager = InvitationModel.objects(__raw__=d)
    invitations = set_manager[n_from:n_to]
    total_count = set_manager.count()

    # wrap invitations
    result = []
    for invitation in invitations:
        result.append({
            'code': invitation['code'],
            'creator': invitation['creator'],
            # 邀请码创建时间
            'create_time': datetime_to_str(invitation['create_time']),
            # 邀请码剩余可用次数
            'available_times': invitation['available_times'],
            # 邀请码有效时间
            'vip_start_time': datetime_to_str(invitation['vip_start_time']),
            'vip_end_time': datetime_to_str(invitation['vip_end_time']),
            # 此邀请码支持的测试次数
            'remaining_exam_num': invitation['remaining_exam_num'],
            'remaining_exercise_num': invitation.remaining_exercise_num,
            # 使用此邀请码的用户
            'activate_users': array2str(invitation['activate_users'], 1)
        })
    return jsonify(errors.success({
        'totalCount': total_count,
        'invitationCodes': result
    }))
