# -*- coding: utf-8 -*-
# Time       : 2019/3/18 16:36
# Author     : tangdaye
# Description: auth util


def validate_email(email):
    import re
    p = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return p.match(email)
