#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime
from flask import current_app, jsonify, request, session
from flask_login import login_user, logout_user, current_user, login_required

from app import errors
from app.auth.util import validate_email, wx_get_user_info, validate_phone, wxlp_get_sessionkey_openid
from app.models.invitation import InvitationModel
from app.models.user import UserModel
from . import auth
# from app.account.views import get_info as get_account_info


@auth.route('/register', methods=['POST'])
def register():
    current_app.logger.info('register request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    if not current_app.config.get('ALLOW_REGISTER'):
        return jsonify(errors.Register_not_allowed)

    username = request.form.get('username').strip().lower()
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    code = request.form.get('code').strip()
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (username and password and name):
        return jsonify(errors.Params_error)
    if current_app.config.get('NEED_INVITATION') and not code:
        return jsonify(errors.Params_error)
    email, phone = '', ''
    # 邮箱注册
    if '@' in username:
        email = username
        if not validate_email(email):
            return jsonify(errors.Params_error)
        existing_user = UserModel.objects(email=email).first()
        if existing_user is not None:
            return jsonify(errors.User_already_exist)
    else:
        phone = username
        if not validate_phone(phone):
            return jsonify(errors.Params_error)
        existing_user = UserModel.objects(phone=phone).first()
        if existing_user is not None:
            return jsonify(errors.User_already_exist)
    # 判断是否需要邀请码
    existing_invitation = None
    if current_app.config.get('NEED_INVITATION'):
        existing_invitation = InvitationModel.objects(code=code).first()
        if existing_invitation is None or existing_invitation.available_times <= 0:
            return jsonify(errors.Illegal_invitation_code)
    # 创建新用户，不要打印志记用户的明文密码！！！
    current_app.logger.info('[NewUser][register]email:%s, phone:%s' % (email, phone))
    new_user = UserModel()
    new_user.email = email.lower() if email != '' else None
    new_user.phone = phone if phone != '' else None
    new_user.set_password(password)
    new_user.name = name
    new_user.last_login_time = datetime.datetime.utcnow()
    new_user.register_time = datetime.datetime.utcnow()
    if current_app.config.get('NEED_INVITATION'):
        new_user.vip_start_time = existing_invitation.vip_start_time
        new_user.vip_end_time = existing_invitation.vip_end_time
        new_user.remaining_exam_num = existing_invitation.remaining_exam_num
        # 这里需要添加一个邀请码信息
        new_user.invitation_code = existing_invitation.code
    else:
        new_user.vip_start_time = datetime.datetime(2020, 6, 1, 10, 0, 0)
        new_user.vip_end_time = datetime.datetime(2020, 8, 15, 10, 0, 0)
        new_user.remaining_exam_num = 100
        new_user.invitation_code = ""

    current_app.logger.info('[UserInfo][register]%s' % new_user.__str__())
    # todo 从这开始需要同步
    new_user.save()
    current_app.logger.info('user(id = %s) has been saved' % new_user.id)

    if current_app.config.get('NEED_INVITATION'):
        # 修改这个邀请码
        existing_invitation.activate_users.append(email if email != '' else phone)
        if existing_invitation.available_times <= 0:
            return jsonify(errors.Invitation_code_invalid)
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
    _time1 = datetime.datetime.utcnow()
    username = request.form.get('username')
    password = request.form.get('password')
    # current_app.logger.debug('login request: %s' % request.form.__str__())
    # current_app.logger.debug('login request current user: %s' % current_user.__str__())

    if current_user.is_authenticated:
        # return jsonify(errors.Already_logged_in)
        check_user = current_user
        current_app.logger.info('re-login user: %s, id: %s' % (check_user.name, check_user.id))
    else:
        """
            校验form，规则
            1. email符合规范
            2. 各项不为空
        """
        _time2 = datetime.datetime.utcnow()
        err, check_user = __authorize(username, password)
        _time3 = datetime.datetime.utcnow()
        if err is not None:
            return jsonify(err)
        current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))

        # 修改最后登录时间
        # check_user.last_login_time = datetime.datetime.utcnow()
        # check_user.save(validate=False)
        # 压力测试，暂时注释掉
        check_user.update(last_login_time=datetime.datetime.utcnow())
        _time4 = datetime.datetime.utcnow()
        login_user(check_user)
        _time5 = datetime.datetime.utcnow()
        current_app.logger.info('[TimeDebug][__authorize]%s' % (_time3 - _time2))
        current_app.logger.info('[TimeDebug][login_user]%s' % (_time5 - _time4))
    _time6 = datetime.datetime.utcnow()
    current_app.logger.info('[TimeDebug][login total]%s' % (_time6 - _time1))
    # return get_account_info()
    return jsonify(errors.success({
        'msg': '登录成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
        'role': str(check_user.role.value)
    }))


@auth.route('/logout', methods=['POST'])
def logout():
    _time1 = datetime.datetime.utcnow()
    # current_app.logger.debug('logout request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        current_app.logger.info('user(id:%s) logout' % current_user.id)
        logout_user()
    _time2 = datetime.datetime.utcnow()
    current_app.logger.info('[TimeDebug][logout total]%s' % (_time2 - _time1))
    return jsonify(errors.success())


@auth.route('/wechat-login')  # callback预留接口，已在微信开放平台登记
def wechat_callback():
    return ''


# web 端微信扫码登录
@auth.route('/wechat/login', methods=['POST'])
def wechat_login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    code = request.form.get('code')
    if not code:
        return jsonify(errors.Params_error)
    err_code, user_info = wx_get_user_info(code, current_app.config['WX_APPID'], current_app.config['WX_SECRET'])
    if err_code:
        return jsonify(errors.error({'code': int(err_code), 'msg': 'invalid wechat code'}))
    wx_union_id = user_info.get('unionid')
    check_user = UserModel.objects(wx_id=wx_union_id).first()
    if not check_user:
        session['wx_union_id'] = wx_union_id
        # data = {'msg': '用户尚未绑定微信，前端请指引用户补充填写信息，进行绑定'}
        # data.update({'userInfo': user_info})
        # return jsonify(errors.error(data))
        headimgurl = user_info.get('headimgurl')
        nickname = user_info.get('nickname').encode('ISO-8859-1').decode('utf-8')  # 要转码
        return jsonify(errors.success({
            'msg': '未绑定用户',
            'headimgurl': headimgurl,
            'nickname': nickname,
        }))
    session['wx_nickname'] = user_info.get('nickname')
    login_user(check_user)
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()
    current_app.logger.info('login from wechat: %s, id: %s' % (check_user.name, check_user.id))
    return jsonify(errors.success({
        'msg': '已绑定用户，自动登录',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
    }))


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
    username = request.form.get('username')
    password = request.form.get('password')
    err, check_user = __authorize(username, password)
    if err is not None:
        return jsonify(err)
    if check_user.wx_id:
        return jsonify(errors.Wechat_already_bind)
    current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))
    login_user(check_user)
    current_app.logger.info('Bind wechat union id -\n  user: %s, union id: %s' % (check_user.email, wx_union_id))
    current_user.wx_id = wx_union_id
    current_user.last_login_time = datetime.datetime.utcnow()
    current_user.save()
    return jsonify(errors.success({
        'msg': '绑定成功，登录成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
    }))


# 微信小程序登录
@auth.route('/wxapp/login', methods=['POST'])
def wxapp_login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    code = request.form.get('code')
    nickName = request.form.get('nick_name')
    if not code:
        return jsonify(errors.Params_error)

    # code -> openid
    err_code, _, openid = wxlp_get_sessionkey_openid(
        code,
        appid=current_app.config['WX_APP_APPID'],
        secret=current_app.config['WX_APP_SECRET']
    )
    if err_code:
        return jsonify(errors.error({'code': int(err_code), 'msg': '获取openid出错'}))

    # todo: 后续 openid 改存 unionid
    check_user = UserModel.objects(wx_id=openid).first()

    # user not exist -> new
    if not check_user:
        new_user = UserModel()
        new_user.name = nickName
        new_user.wx_id = openid
        new_user.last_login_time = datetime.datetime.utcnow()
        new_user.register_time = datetime.datetime.utcnow()
        new_user.save()
        check_user = new_user

    login_user(check_user)
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()
    current_app.logger.info('wxapp login: %s, id: %s' % (check_user.name, check_user.id))
    return jsonify(errors.success({
        'msg': '登录成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
    }))


def __authorize(username, password):
    """
    使用 username 和 password 验证用户
    :type username: str
    :type password: str
    :return: 返回一个tuple： (err, check_user)
        err 为 errors 中定义的错误类型（dict）
        check_user 为数据库中检索到的用户对象
        若通过, err 为 None
        若验证不通过, check_user 为 None
    """
    if not (username and password):
        return errors.Params_error, None
    username = username.strip().lower()
    password = password.strip()
    if '@' in username:
        # 邮箱登录
        if not validate_email(username):
            return errors.Params_error, None
        check_user = UserModel.objects(email=username).first()
    else:
        # 手机号登录
        if not validate_phone(username):
            return errors.Params_error, None
        check_user = UserModel.objects(phone=username).first()
    if not check_user:
        return errors.User_not_exist, None
    if (not current_app.config['IGNORE_LOGIN_PASSWORD']) and (not check_user.check_password(password)):
        return errors.Authorize_failed, None
    return None, check_user
