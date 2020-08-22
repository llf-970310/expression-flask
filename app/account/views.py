#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向用户的accounts相关views,与view无关的具体功能的实现请写在utils.py中,在此尽量只作引用

from flask import request, current_app, jsonify
from flask_login import current_user, login_required

from app import errors
from app.exam.manager.exam import get_exam_by_id, get_score_and_feature
from app.exam.manager.report import generate_report
from . import account

from app.models.exam import HistoryTestModel, CurrentTestModel
from app.admin.admin_config import ScoreConfig
from app.utils.date_and_time import datetime_to_str
from app.paper import compute_exam_score
from app.models.invitation import InvitationModel


@account.route('/update', methods=['POST'])
@login_required
def update():
    password = request.form.get('password')
    name = request.form.get('name').strip()
    if len(name) > 20:
        return jsonify(errors.Params_error)
    if not password:
        current_user.name = name
    elif password.strip() == "":
        return jsonify(errors.Params_error)
    else:
        current_user.set_password(password)
        current_user.name = name
    current_user.save()
    return jsonify(errors.success({
        'msg': '修改成功',
        'uuid': str(current_user.id),
        'name': str(current_user.name),
        'password': '********'
    }))


@account.route('/update-privilege/<code>', methods=['POST'])
@login_required
def update_privilege(code):
    # todo 从这开始需要同步
    existing_invitation = InvitationModel.objects(code=code).first()
    if existing_invitation is None or existing_invitation.available_times <= 0:
        return jsonify(errors.Illegal_invitation_code)
    # 修改这个邀请码
    existing_invitation.activate_users.append(current_user.email if current_user.email else current_user.phone)
    if existing_invitation.available_times <= 0:
        return jsonify(errors.Invitation_code_invalid)
    existing_invitation.available_times -= 1
    current_app.logger.debug('invitation info: %s' % existing_invitation.__str__())
    existing_invitation.save()
    # todo 同步结束
    current_app.logger.info('[UpdatePrivilege][update_privilege]email:%s, phone:%s' %
                            (current_user.email, current_user.phone))
    current_user.vip_start_time = existing_invitation.vip_start_time
    current_user.vip_end_time = existing_invitation.vip_end_time
    current_user.remaining_exam_num = existing_invitation.remaining_exam_num
    # 这里需要添加一个邀请码信息
    current_user.invitation_code = existing_invitation.code
    current_app.logger.info('[UserInfo][update_privilege]%s' % current_user.__str__())
    current_user.save()
    current_app.logger.debug('user(id = %s) has been saved' % current_user.id)
    return jsonify(errors.success())


@account.route('/unbind-wx', methods=['POST'])
@login_required
def unbind_wx():
    if not current_user.wx_id:
        return jsonify(errors.Wechat_not_bind)
    current_user.update(set__wx_id='')
    return jsonify(errors.success(
        {
            'msg': '解绑成功'
        }
    ))


@account.route('/info', methods=['GET'])
@login_required
def get_info():
    current_app.logger.debug('[GetAccountInfo][get_info]%s' % current_user)
    return jsonify(errors.success({
        'role': str(current_user.role.value),
        'name': current_user.name,
        'email': current_user.email if current_user.email is not None else current_user.phone,
        'password': '********',
        'register_time': datetime_to_str(current_user.register_time),
        'last_login_time': datetime_to_str(current_user.last_login_time),
        # 'questions_history': current_user.questions_history,
        'wx_id': current_user.wx_id,
        'vip_start_time': datetime_to_str(current_user.vip_start_time),
        'vip_end_time': datetime_to_str(current_user.vip_end_time),
        'remaining_exam_num': current_user.remaining_exam_num
    }))


# TODO: 接口可以在这里，但评分逻辑应该单独抽取出来
@account.route('/history-scores/<tpl_id>', methods=['GET'])
@account.route('/history-scores', methods=['GET'])
@login_required
def get_history_scores(tpl_id="0"):
    # 查看所有历史成绩
    if tpl_id == "0":
        history_scores_origin = HistoryTestModel.objects(user_id=str(current_user.id)).order_by("test_start_time")
        current_scores_origin = CurrentTestModel.objects(user_id=str(current_user.id)).order_by("test_start_time")
    # 查看指定模板的历史成绩
    else:
        history_scores_origin = HistoryTestModel.objects(user_id=str(current_user.id), paper_tpl_id=tpl_id).order_by("test_start_time")
        current_scores_origin = CurrentTestModel.objects(user_id=str(current_user.id), paper_tpl_id=tpl_id).order_by("test_start_time")

    history_scores = []
    for history in history_scores_origin:
        history_score_item = {
            "test_start_time": datetime_to_str(history["test_start_time"]),
            "paper_tpl_id": history["paper_tpl_id"],
            "test_id": history["current_id"]
        }

        score_format = {}
        if history["score_info"]:
            for k, v in history["score_info"].items():
                score_format[k] = format(v, ScoreConfig.DEFAULT_NUM_FORMAT)
        else:
            for k in ["音质", "结构", "逻辑", "细节", "主旨", "total"]:
                score_format[k] = format(0, ScoreConfig.DEFAULT_NUM_FORMAT)

        history_score_item["score_info"] = score_format
        history_scores.append(history_score_item)

    for current in current_scores_origin:
        questions = current['questions']
        if __question_all_finished(questions):  # 全部结束才录入history
            # 所有题目已完成但没有分数信息，则计算分数
            if not current['score_info']:
                score = {}
                for k, v in questions.items():
                    score[int(k)] = v['score']
                current['score_info'] = compute_exam_score(score, current.paper_type)
                current.save()

            score_format = {}
            for k, v in current["score_info"].items():
                score_format[k] = format(v, ScoreConfig.DEFAULT_NUM_FORMAT)

            history_scores.append({
                "test_start_time": datetime_to_str(current["test_start_time"]),
                "test_id": str(current["id"]),
                "score_info": score_format,
                "paper_tpl_id": current["paper_tpl_id"],
            })

    if len(history_scores) == 0:
        return jsonify(errors.No_history)
    return jsonify(errors.success({"history": history_scores}))


@account.route('/history-report/<test_id>', methods=['GET'])
@login_required
def get_history_report(test_id):
    test = get_exam_by_id(test_id)
    if test is None:
        return jsonify(errors.Exam_not_exist)

    questions = test['questions']
    handling, score, feature = get_score_and_feature(questions)
    if handling:
        return jsonify(errors.WIP)
    else:
        report = generate_report(feature, score, test.paper_type)
        # 为了与 get_result 接口保持统一，这里用了 data 做字段，实际是分数信息
        result = {"report": report, "data": test['score_info']}
        return jsonify(errors.success(result))


def __question_all_finished(question_dict):
    for value in question_dict.values():
        if value['status'] != 'finished' and value['status'] != 'error':
            return False
    return True
