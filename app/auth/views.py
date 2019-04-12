#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime
import json
import requests
from flask import current_app, jsonify, request, session, url_for
from flask_login import login_user, logout_user, current_user

from app.models.exam import CurrentTestModel
from app.models.user import UserModel
from app.models.invitation import InvitationModel
from app.auth.util import *
from flask import redirect

from . import auth
from app import errors


def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


@auth.route('/user/info', methods=['GET'])
def user_info():
    current_app.logger.info('get user info request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.success({
            'role': str(current_user.role.value),
            'name': current_user.name,
            'email':current_user.email,
            'password': current_user.password,
            'register_time':datetime_toString(current_user.register_time),
            'last_login_time':datetime_toString(current_user.last_login_time),
            'questions_history':current_user.questions_history,
            'wx_id':current_user.wx_id,
            'vip_start_time':datetime_toString(current_user.vip_start_time),
            'vip_end_time':datetime_toString(current_user.vip_end_time),
            'remaining_exam_num':current_user.remaining_exam_num

        }))
    else:
        return jsonify(errors.Authorize_needed)


@auth.route('/update',methods=['POST'])
def update():
    if current_user.is_authenticated:
        email=current_user.email
    else:
        return jsonify(errors.Authorize_needed)
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    if not password:
        return jsonify(errors.Params_error)
    check_user = UserModel.objects(email=email).first()
    check_user.password=current_app.md5_hash(password)
    check_user.name=name
    check_user.save()
    return jsonify(errors.success({
        'msg': '修改成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
        'password':str(check_user.password)
    }))


@auth.route('/untying',methods=['POST'])
def untying():
    if current_user.is_authenticated:
        email = current_user.email
    else:
        return jsonify(errors.Authorize_needed)
    check_user=UserModel.objects(email=email).first()
    if not check_user.wx_id:
        return jsonify(errors.Wechat_not_bind)
    check_user.wx_id=''
    check_user.save()
    return  jsonify(errors.success(
        {
            'msg':'解绑成功'
        }
    ))


@auth.route('/showscore',methods=['POST'])
def showscore():
    if current_user.is_authenticated:
        email = current_user.email
    else:
        return jsonify(errors.Authorize_needed)
    check_user = UserModel.objects(email=email).first()
    user_id=check_user.id
    scorelist=CurrentTestModel.objects(user_id=user_id)
    # if scorelist.count()==0:
    #     return jsonify(errors.No_history)
    return jsonify(errors.success(scorelist))


@auth.route('/register', methods=['POST'])
def register():
    current_app.logger.info('register request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    if not current_app.config.get('ALLOW_REGISTER'):
        return jsonify(errors.Register_not_allowed)

    email = request.form.get('email').strip().lower()
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    code = request.form.get('code').strip()
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (email and password and name and code):
        return jsonify(errors.Params_error)
    if not validate_email(email):
        return jsonify(errors.Params_error)
    existing_user = UserModel.objects(email=email).first()
    if existing_user is not None:
        return jsonify(errors.User_already_exist)
    existing_invitation = InvitationModel.objects(code=code).first()
    if existing_invitation is None or existing_invitation.available_times <= 0:
        return jsonify(errors.Illegal_invitation_code)
    new_user = UserModel()
    new_user.email = email.lower()
    new_user.password = current_app.md5_hash(password)
    new_user.name = name
    new_user.last_login_time = datetime.datetime.utcnow()
    new_user.register_time = datetime.datetime.utcnow()
    new_user.vip_start_time = existing_invitation.vip_start_time
    new_user.vip_end_time = existing_invitation.vip_end_time
    new_user.remaining_exam_num = existing_invitation.remaining_exam_num
    current_app.logger.info('user info: %s' % new_user.__str__())
    # todo 从这开始需要同步
    new_user.save()
    current_app.logger.info('user(id = %s) has been saved' % new_user.id)

    # 修改这个邀请码
    existing_invitation.activate_users.append(name)
    existing_invitation.available_times -= 1
    current_app.logger.info('invitation info: %s' % existing_invitation.__str__())
    existing_invitation.save()
    # todo 同步到这结束
    current_app.logger.info('invitation(id = %s) has been saved' % existing_invitation.id)

    login_user(new_user)  # 直接登录？好吧

    return jsonify(errors.success({
        'msg': '注册成功，已自动登录',
        'uuid': str(new_user.id),
        'name': str(new_user.name)
    }))


@auth.route('/login', methods=['POST'])
def login():
    current_app.logger.info('login request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    email = request.form.get('username')
    password = request.form.get('password')
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (email and password):
        return jsonify(errors.Params_error)
    if not validate_email(email):
        return jsonify(errors.Params_error)
    check_user = UserModel.objects(email=email).first()
    if not check_user:
        return jsonify(errors.Authorize_failed)
    if (not current_app.config['IGNORE_LOGIN_PASSWORD']) and (check_user.password != current_app.md5_hash(password)):
        return jsonify(errors.Authorize_failed)
    login_user(check_user)
    current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()  # 修改最后登录时间
    # !important
    return jsonify(errors.success({
        'msg': '登录成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
    }))


@auth.route('/logout', methods=['POST'])
def logout():
    current_app.logger.info('logout request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        current_app.logger.info('user(id:%s) logout' % current_user.id)
        logout_user()
        return jsonify(errors.success())
    else:
        return jsonify(errors.Authorize_needed)


@auth.route('/wechat-login')  # callback预留接口，已在微信开放平台登记
def wechat_callback():
    return ''


@auth.route('/wechat/params', methods=['GET', 'POST'])
def wechat_params():  # todo: as api
    redirect_url = 'https://expression.iselab.cn%s' % url_for('auth.wechat_login')
    data = {'appId': current_app.config['WX_APPID'], 'redirectUrl': redirect_url}
    return str(data) + '<br>' \
                       '<a href="https://open.weixin.qq.com/connect/qrconnect?appid={0}&redirect_uri={1}' \
                       '&response_type=code&scope=snsapi_login&state=zidingyineirong#wechat_redirect">微信登录</a> ' \
                       '（请把这个嵌入前端页面,使用ajax获取二维码并展示）<br>' \
                       '（详见：https://open.weixin.qq.com/cgi-bin/showdocument?' \
                       'action=dir_list&t=resource/res_list&verify=1&id=open1419316505&token=&lang=zh_CN ' \
                       '示例部分）'.format(current_app.config['WX_APPID'], redirect_url)
    return jsonify(errors.success(data))
    # 扫描并确认后浏览器被重定向到:
    # https://expression.iselab.cn/api/auth/login/wechat?code=061gOGry17jDx90iRjty16tBry1gOGrZ&state=zidingyineirong


@auth.route('/wechat/login')
def wechat_login():
    if current_user.is_authenticated:
        # return jsonify(errors.Already_logged_in)
        return redirect('/')
    code = request.args.get('code')
    if not code:
        return jsonify(errors.Params_error)
    oauth2_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&' \
                 'grant_type=authorization_code'.format(current_app.config['WX_APPID'],
                                                        current_app.config['WX_SECRET'], code)
    oauth2_ret = json.loads(requests.get(oauth2_url).text)
    err_code = oauth2_ret.get('errcode')
    if err_code:
        return jsonify(errors.error({'code': int(err_code), 'msg': oauth2_ret.get('errmsg')}))
    token = oauth2_ret.get('access_token')
    openid = oauth2_ret.get('openid')

    user_info_url = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}'.format(token, openid)
    user_info = json.loads(requests.get(user_info_url).text)
    wx_union_id = user_info.get('unionid')
    check_user = UserModel.objects(wx_id=wx_union_id).first()
    if not check_user:
        session['wx_union_id'] = wx_union_id
        # data = {'msg': '用户尚未绑定微信，前端请指引用户补充填写信息，进行绑定'}
        # data.update({'userInfo': user_info})
        # return jsonify(errors.error(data))
        headimgurl = user_info.get('headimgurl')
        nickname = user_info.get('nickname')
        return redirect("/#/login-wechat?headimgurl=%s&nickname=%s" % (headimgurl, nickname))
    session['wx_token'] = oauth2_ret.get('access_token')
    session['wx_openid'] = oauth2_ret.get('openid')
    session['wx_nickname'] = user_info.get('nickname')
    login_user(check_user)
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()
    current_app.logger.info('login from wechat: %s, id: %s' % (check_user.name, check_user.id))
    return redirect('/')


"""
微信登录返回示例
oauth2 ret:
{"access_token":"19_IJE6MpX1MyK9VVXQlppGJk762p_n80ePdS0oWHVhyx7vCUwdWWkolumWFnaYOp3QBlJD5k9x-vNaejZAoSlsZg",
 "expires_in":7200,
 "refresh_token":"19_IlD6dnGYZKUchv-G92SZvxkqRjAs_JdLuow2FTduYc9wVtO6esEb_LzkbQBdmApuKnuAEY-1V8zUkETeZxWxeg",
 "openid":"oSeg251hPU-NlMesh7KrT7Izp-Bc",
 "scope":"snsapi_login",
 "unionid":"om7mj00CPmlmh27SaLSFu3Nd_RQA"}
user_info: 
{'openid': 'oSeg251hPU-NlMesh7KrT7Izp-Bc',
 'nickname': 'BetweenAugust&December', 'sex': 1, 'language': 'zh_CN',
 'city': 'Nanjing', 'province': 'Jiangsu', 'country': 'CN',
 'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLST3pS1ya049yK1vpfF7O8NV96S2GKrrvopiaRR5DQvuK9G4Jmk6iceDjTcYwF62yx1H9vKSI89qxg/132',
 'privilege': [], 'unionid': 'om7mj00CPmlmh27SaLSFu3Nd_RQA'}
"""


@auth.route('/wechat/bind', methods=['POST'])
def wechat_bind():
    """
    前端展示用户的微信头像和名称，引导用户填写账号和密码进行绑定，将来可能直接绑定手机号
    :return:
    """
    wx_union_id = session.get('wx_union_id')
    if not wx_union_id:
        return jsonify(errors.error())
    email = request.form.get('email')
    phone = request.form.get('phone')  # todo:手机号
    password = request.form.get('pwd')
    if not (email and password):
        return jsonify(errors.Params_error)

    check_user = UserModel.objects(email=email).first()
    if not check_user:
        return jsonify(errors.Authorize_failed)
    if (not current_app.config['IGNORE_LOGIN_PASSWORD']) and (check_user.password != current_app.md5_hash(password)):
        return jsonify(errors.Authorize_failed)

    if check_user.wx_id:
        return jsonify(errors.Wechat_already_bind)
    current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))
    login_user(check_user)
    current_app.logger.info('Bind wechat union id -\n  user: %s, union id: %s' % (check_user.email, wx_union_id))
    current_user.wx_id = wx_union_id
    current_user.last_login_time = datetime.datetime.utcnow()
    current_user.save()
    resp = {'msg': '绑定成功，登录成功', 'user_id': str(check_user.id), 'role': str(check_user.role)}
    return jsonify(errors.success(resp))
