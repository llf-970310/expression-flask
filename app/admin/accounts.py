#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向管理员的accounts相关views,与view无关的具体功能的实现请写在app/accounts/utils.py中,在此尽量只作引用

from flask import jsonify

from app import errors
from . import admin


@admin.route('/accounts/test', methods=['GET', 'POST'])  # url will be .../admin/accounts/test
def accounts_test():
    return jsonify(errors.success({'data': 'admin: accounts test'}))
