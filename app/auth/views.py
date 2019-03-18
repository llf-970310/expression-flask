#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime
from flask import current_app, jsonify, request
from flask_login import login_user, logout_user, current_user
from app.models.user import UserModel
from app.models.invitation import InvitationModel
from app.auth.util import *

from . import auth
from app import errors


@auth.route('/register', methods=['POST'])
def register():
    current_app.looger.info('register request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    if not current_app.config.get('ALLOW_REGISTER'):
        return jsonify(errors.Register_not_allowed)

    email = request.form.get('email').strip().lower()
    password = request.form.get('pwd').strip()
    name = request.form.get('name').strip()
    code = request.form.get('code').strip()
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (email and password and name and code):
        return jsonify(errors.Params_error)
    if not validate_email(email):
        return jsonify(errors.Params_error)
    existing_user = UserModel.objects(email=email).first()
    if existing_user is not None:
        return jsonify(errors.User_already_exist)
    existing_invitation = InvitationModel.objects(code=code).first()
    if existing_invitation is None or existing_invitation.remaining_exam_num <= 0:
        return jsonify(errors.Illegal_invitation_code)
    new_user = UserModel()
    new_user.email = email.lower()
    new_user.password = current_app.md5_hash(password)
    new_user.name = name
    new_user.last_login_time = datetime.datetime.utcnow()
    new_user.register_time = datetime.datetime.utcnow()
    new_user.vip_start_time = existing_invitation.vip_start_time
    new_user.vip_end_time = existing_invitation.vip_end_time
    new_user.remaining_exam_num = existing_invitation.remaining_exam_num
    current_app.looger.info('user info: %s' % new_user.__str__())
    # todo 从这开始需要同步
    new_user.save()
    current_app.looger.info('user(id = %s) has been saved' % new_user.id)

    # 修改这个邀请码
    existing_invitation.activate_users.append(name)
    existing_invitation.available_times -= 1
    current_app.looger.info('invitation info: %s' % existing_invitation.__str__())
    existing_invitation.save()
    # 同步到这结束
    current_app.looger.info('invitation(id = %s) has been saved' % existing_invitation.id)

    login_user(new_user)  # 直接登录？好吧

    return jsonify(errors.success({'msg': '注册成功，已自动登录', 'user_id': str(new_user.id)}))


@auth.route('/login', methods=['POST'])
def login():
    current_app.looger.info('login request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    email = request.form.get('email')
    # name = request.form.get('name')
    password = request.form.get('pwd')
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (email and password):
        return jsonify(errors.Params_error)
    if not validate_email(email):
        return jsonify(errors.Params_error)
    check_user = UserModel.objects(email=email).first()
    if (not current_app.config['NOT_CHECK_LOGIN_PASSWORD']) and (check_user.password != current_app.md5_hash(password)):
        return jsonify(errors.Authorize_failed)
    login_user(check_user)
    current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()  # 修改最后登录时间
    # !important
    return jsonify(errors.success(
        {'msg': '登录成功', 'user_id': str(check_user.id), 'role': str(check_user.role)}))  # role : default | admin


@auth.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify(errors.success())
    else:
        return jsonify(errors.Authorize_needed)

# @auth.route('/dashboard')
# def dashboard():
#     if current_user.is_authenticated:
#         return jsonify({'name': current_user.name, 'email': current_user.email})
#     else:
#         return jsonify(errors.Authorize_needed)
