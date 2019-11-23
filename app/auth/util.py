# -*- coding: utf-8 -*-
# Time       : 2019/3/18 16:36
# Author     : tangdaye
# Description: auth util

from functools import wraps
from flask import jsonify
from flask_login import login_required, current_user
from app import errors


def validate_email(email):
    import re
    p = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return p.match(email)


def admin_login_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify(errors.Admin_login_required)
        return func(*args, **kwargs)
    return decorated_view
