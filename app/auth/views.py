#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime
from flask import current_app, jsonify, session, request
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from app.models.user import UserModel

from . import auth
from app import errors


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    if not current_app.config['ALLOW_REGISTER']:
        return jsonify(errors.Register_not_allowed)
    email = request.form.get('email').upper().strip(' ')
    password = request.form.get('pwd')
    name = request.form.get('name')
    if not (name and password and email):  # all should be none empty str type
        # todo: validate email format
        return jsonify(errors.Params_error)

    existing_user = UserModel.objects(email=email).first()
    if existing_user is None:
        new_user = UserModel()
        new_user.email = email.lower()
        new_user.password = current_app.md5_hash(password)
        new_user.name = name
        new_user.last_login_time = datetime.datetime.utcnow()
        new_user.register_time = datetime.datetime.utcnow()
        new_user.save()
        login_user(new_user)
        return jsonify(errors.success())
    else:
        return jsonify(errors.User_already_exist)


@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    name = request.form.get('name')
    password = request.form.get('pwd')
    student_id = request.form.get('student_id')

    if not (name and password and student_id):  # all should be none empty str type
        return jsonify(errors.Params_error)

    student_id = student_id.upper().strip(' ')

    current_app.logger.info('login student_name: %s, student_id: %s' % (str(name), str(student_id)))

    check_user = UserModel.objects(student_id=student_id).first()  # todo: student_id should be migrated
    if check_user:
        if check_user['password'] == current_app.md5_hash(password) or current_app.config['NOT_CHECK_LOGIN_PASSWORD']:
            login_user(check_user)
            check_user.last_login_time = datetime.datetime.utcnow()
            check_user.save()
            # init session
            session['user_name'] = name
            session['student_id'] = student_id
            session['question_num'] = 0
            session['new_test'] = True
            session['user_id'] = check_user.id.__str__()
            session['test_id'] = '000000000000000000000000'
            return jsonify(errors.success())
        return jsonify(errors.Authorize_failed)
    else:
        return jsonify(errors.User_not_exist)


@auth.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        return jsonify({'name': current_user.name, 'email': current_user.email})
    else:
        return jsonify(errors.Authorize_needed)


@auth.route('/logout', methods=['POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify(errors.success())
