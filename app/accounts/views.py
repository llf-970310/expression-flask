#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向用户的accounts相关views,与view无关的具体功能的实现请写在utils.py中,在此尽量只作引用

from flask import jsonify

from app import errors
from . import accounts


@accounts.route('/test', methods=['GET', 'POST'])  # url will be .../accounts/test
def accounts_test():
    return jsonify(errors.success())
