#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

from . import exam
from app.models.user import User
from flask import redirect, url_for, current_app
from flask_login import login_required, current_user
