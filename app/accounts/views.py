#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向用户的accounts相关views,与view无关的具体功能的实现请写在utils.py中,在此尽量只作引用

from flask import request, current_app, jsonify, session
from flask_login import current_user

from app import errors
from . import accounts


@accounts.route('/display', methods=['GET'])
def account_display():
    exams = current_user.exam_history
    return jsonify(errors.success())


@accounts.route('/modify', methods=['POST'])
def accounts_modify():
    return jsonify(errors.success())
