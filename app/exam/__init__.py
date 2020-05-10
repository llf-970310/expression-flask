#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

from flask import Blueprint

exam = Blueprint('exam', __name__)

from . import views
from . import wxmp_views
from . import wxmp_batch_test_views
