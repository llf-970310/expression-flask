#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-26

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import accounts
from . import exam
from . import optimize
from . import question
