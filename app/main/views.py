#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-22

from . import main
from flask import redirect


@main.route('/')
@main.route('/index')
def index():
    return redirect('/index.html')
