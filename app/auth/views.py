#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime
import json

import requests
from flask import current_app, jsonify, request, session
from flask_login import login_user, logout_user, current_user, login_required

from app import errors
from app.admin.admin_config import ScoreConfig
from app.admin.util import convert_datetime_to_str
from app.auth.util import validate_email
from app.models.exam import HistoryTestModel, CurrentTestModel
from app.models.invitation import InvitationModel
from app.models.user import UserModel
from . import auth


@auth.route('/user/info', methods=['GET'])
@login_required
def user_info():
    current_app.logger.info('get user info request: %s' % request.form.__str__())
    print(current_user)
    return jsonify(errors.success({
        'role': str(current_user.role.value),
        'name': current_user.name,
        'email': current_user.email,
        'password': current_user.password,
        'register_time': convert_datetime_to_str(current_user.register_time),
        'last_login_time': convert_datetime_to_str(current_user.last_login_time),
        'questions_history': current_user.questions_history,
        'wx_id': current_user.wx_id,
        'vip_start_time': convert_datetime_to_str(current_user.vip_start_time),
        'vip_end_time': convert_datetime_to_str(current_user.vip_end_time),
        'remaining_exam_num': current_user.remaining_exam_num

    }))


@auth.route('/update', methods=['POST'])
def update():
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    check_user = __get_check_user_from_db(current_user)
    if not password:
        check_user.name = name
    else:
        check_user.password = current_app.md5_hash(password)
        check_user.name = name
    check_user.save()
    return jsonify(errors.success({
        'msg': '修改成功',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
        'password': str(check_user.password)
    }))


@auth.route('/untying', methods=['POST'])
def untying():
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    check_user = __get_check_user_from_db(current_user)
    if not check_user.wx_id:
        return jsonify(errors.Wechat_not_bind)
    check_user.wx_id = ''
    check_user.save()
    return jsonify(errors.success(
        {
            'msg': '解绑成功'
        }
    ))


@auth.route('/showscore', methods=['POST'])
def showscore():
    if not current_user.is_authenticated:
        return jsonify(errors.Login_required)
    check_user = __get_check_user_from_db(current_user)
    history_scores_origin = HistoryTestModel.objects(user_id=str(check_user['id']))
    current_scores_origin = CurrentTestModel.objects(user_id=str(check_user['id']))
    history_scores = []
    for history in history_scores_origin:
        if history["score_info"]:
            history_scores.append({
                "test_start_time": convert_datetime_to_str(history["test_start_time"]),
                # "paper_type": history["paper_type"],
                "score_info": {
                    "音质": format(history["score_info"]["音质"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "结构": format(history["score_info"]["结构"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "逻辑": format(history["score_info"]["逻辑"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "细节": format(history["score_info"]["细节"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "主旨": format(history["score_info"]["主旨"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "total": format(history["score_info"]["total"], ScoreConfig.DEFAULT_NUM_FORMAT),
                },
                # "all_analysed": history["all_analysed"],
            })
        else:
            history_scores.append({
                "test_start_time": convert_datetime_to_str(history["test_start_time"]),
                # "paper_type": history["paper_type"],
                "score_info": {
                    "音质": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                    "结构": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                    "逻辑": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                    "细节": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                    "主旨": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                    "total": format(0, ScoreConfig.DEFAULT_NUM_FORMAT),
                },
                # "all_analysed": history["all_analysed"],
            })

    for current in current_scores_origin:
        questions = current['questions']
        if __question_all_finished(questions):  # 全部结束才录入history
            history_scores.append({
                "test_start_time": convert_datetime_to_str(current["test_start_time"]),
                "score_info": {
                    "音质": format(current["score_info"]["音质"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "结构": format(current["score_info"]["结构"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "逻辑": format(current["score_info"]["逻辑"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "细节": format(current["score_info"]["细节"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "主旨": format(current["score_info"]["主旨"], ScoreConfig.DEFAULT_NUM_FORMAT),
                    "total": format(current["score_info"]["total"], ScoreConfig.DEFAULT_NUM_FORMAT),
                },
            })

    if len(history_scores) == 0:
        return jsonify(errors.No_history)
    return jsonify(errors.success({"history": history_scores}))


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
    if not (username and password and name and code):
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
        existing_user = UserModel.objects(phone=phone).first()
        if existing_user is not None:
            return jsonify(errors.User_already_exist)
    existing_invitation = InvitationModel.objects(code=code).first()
    if existing_invitation is None or existing_invitation.available_times <= 0:
        return jsonify(errors.Illegal_invitation_code)
    print("email: " + email + " phone: " + phone)
    print("passsword: " + password)
    new_user = UserModel()
    new_user.email = email.lower() if email != '' else None
    new_user.phone = phone if phone != '' else None
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
    current_app.logger.info('login request: %s' % request.form.__str__())
    current_app.logger.info('login request current user: %s' % current_user.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    username = request.form.get('username')
    password = request.form.get('password')
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    err, check_user = __authorize(username, password)
    if err is not None:
        return jsonify(err)
    login_user(check_user)
    current_app.logger.info('login user: %s, id: %s' % (check_user.name, check_user.id))
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()  # 修改最后登录时间
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


@auth.route('/wechat-login')  # callback预留接口，已在微信开放平台登记
def wechat_callback():
    return ''


@auth.route('/wechat/login', methods=['POST'])
def wechat_login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    code = request.form.get('code')
    if not code:
        return jsonify(errors.Params_error)
    oauth2_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&' \
                 'grant_type=authorization_code'.format(current_app.config['WX_APPID'],
                                                        current_app.config['WX_SECRET'], code)
    oauth2_ret = json.loads(requests.get(oauth2_url).text)
    err_code = oauth2_ret.get('errcode')
    if err_code:
        return jsonify(errors.error({'code': int(err_code), 'msg': 'invalid wechat code'}))
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
        nickname = user_info.get('nickname').encode('ISO-8859-1').decode('utf-8')  # 要转码
        return jsonify(errors.success({
            'msg': '未绑定用户',
            'headimgurl': headimgurl,
            'nickname': nickname,
        }))
    session['wx_token'] = oauth2_ret.get('access_token')
    session['wx_openid'] = oauth2_ret.get('openid')
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


def __get_check_user_from_db(current_user):
    """
    根据登录的用户获取当前数据库中用户
    :param email_or_phone: 当前登录用户
    :return: 当前用户
    """
    email = current_user.email
    if email is None:
        phone = current_user.phone
        check_user = UserModel.objects(phone=phone).first()
    else:
        check_user = UserModel.objects(email=email).first()
    return check_user


def __question_all_finished(question_dict):
    for value in question_dict.values():
        if value['status'] != 'finished':
            return False
    return True


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
    username = username.strip().lower()
    password = password.strip()
    if not (username and password):
        return errors.Params_error, None
    if '@' in username:
        # 邮箱登录
        email = username
        if not validate_email(email):
            return errors.Params_error, None
        check_user = UserModel.objects(email=email).first()
    else:
        # 手机号登录
        phone = username
        check_user = UserModel.objects(phone=phone).first()
    if not check_user:
        return errors.Authorize_failed, None
    if (not current_app.config['IGNORE_LOGIN_PASSWORD']) and (check_user.password != current_app.md5_hash(password)):
        return errors.Authorize_failed, None
    return None, check_user
