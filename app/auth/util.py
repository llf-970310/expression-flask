# -*- coding: utf-8 -*-
# Time       : 2019/3/18 16:36
# Author     : tangdaye
# Description: auth util

from functools import wraps
import json
import requests
from flask import jsonify
from flask_login import login_required, current_user
from app import errors


def validate_email(email):
    import re
    p = re.compile(r"^[A-Za-z0-9]+([_\.][A-Za-z0-9]+)*@([A-Za-z0-9\-]+\.)+[A-Za-z]{2,6}$")
    return p.match(email)


def validate_phone(phone):
    import re
    p = re.compile(r"^1[3-9]\d{9}$")
    return p.match(phone)


def admin_login_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify(errors.Admin_login_required)
        return func(*args, **kwargs)
    return decorated_view


def wx_get_token_openid(code: str, appid, secret):
    oauth2_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&' \
                 'grant_type=authorization_code'.format(appid, secret, code)
    oauth2_ret = json.loads(requests.get(oauth2_url).text)
    err_code = oauth2_ret.get('errcode')
    if err_code:
        return err_code, None, None
    token = oauth2_ret.get('access_token')
    openid = oauth2_ret.get('openid')
    return 0, token, openid


def wx_get_user_info(code: str, appid, secret):
    err_code, token, openid = wx_get_token_openid(code, appid, secret)
    if err_code:
        return err_code, None
    _user_info_url = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}'.format(token, openid)
    _user_info = json.loads(requests.get(_user_info_url).text)
    return 0, _user_info


def wx_get_union_id(user_info: dict):
    return user_info.get('unionid')


def wxlp_get_sessionkey_openid(code: str, appid, secret):
    openid_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&' \
                 'grant_type=authorization_code'.format(appid, secret, code)
    ret = json.loads(requests.get(openid_url).text)
    err_code = ret.get('errcode', 0)
    if err_code:
        return err_code, None, None
    session_key = ret.get('session_key')
    openid = ret.get('openid')
    return 0, session_key, openid


# if __name__ == '__main__':
#     appid = 'wx23f0c43d3ca9ed9d'
#     secret = '3d791d2ef69556abb746da30df4aa8e6'
#     code = '033v3nC50zvB5D1nctF50LecC50v3nCi'
#     # print(wx_get_user_info(code, appid, secret)
#     print(wxlp_get_sessionkey_openid(code, appid, secret))
#     # {'session_key': 'a0WJqDaFiKsvVhhWax9fUQ==', 'openid': 'oMQ7Y5UTBxgwgtT9NXH0aFxy6_aQ'}
