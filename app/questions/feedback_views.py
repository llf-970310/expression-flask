#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-03-08

import datetime
from flask import jsonify, current_app
from flask_login import current_user, login_required

from app import errors
from . import questions
from .utils import get_question_obj


# TODO: 使用redis锁限制每天只能赞一次


@questions.route('/<q_dbid>/like', methods=['POST'])
@login_required
def new_like(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    if str(question.id) in current_user.questions_liked:
        return jsonify(errors.success())

    question.feedback_likes += 1
    question.save()
    like_time = datetime.datetime.utcnow()
    current_user.questions_liked.update({q_dbid: like_time})
    current_user.save()
    current_app.logger.info('[NewLike][feedback_views]%s liked question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/like', methods=['DELETE'])
@login_required
def cancel_like(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    if str(question.id) not in current_user.questions_liked:
        return jsonify(errors.success())

    question.feedback_likes -= 1
    question.save()
    current_user.questions_liked.pop(q_dbid)
    current_user.save()
    current_app.logger.info('[LikeCanceled][feedback_views]%s canceled like for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/up', methods=['POST'])
@login_required
def new_up(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_ups += 1
    question.save()
    current_app.logger.info('[NewUp][feedback_views]%s gave an up for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/up', methods=['DELETE'])
@login_required
def cancel_up(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_ups -= 1
    question.save()
    current_app.logger.info('[UpCanceled][feedback_views]%s canceled an up for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/down', methods=['POST'])
@login_required
def new_down(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_downs += 1
    question.save()
    current_app.logger.info('[NewDown][feedback_views]%s gave a down for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/down', methods=['DELETE'])
@login_required
def cancel_down(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_downs -= 1
    question.save()
    current_app.logger.info('[DownCanceled][feedback_views]%s canceled a down for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/up2down', methods=['POST'])
@login_required
def up2down(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_ups -= 1
    question.feedback_downs += 1
    question.save()
    current_app.logger.info('[Up2Down][feedback_views]%s gave an up2down for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())


@questions.route('/<q_dbid>/down2up', methods=['POST'])
@login_required
def down2up(q_dbid):
    question, err = get_question_obj(q_dbid)
    if err:
        return jsonify(err)
    question.feedback_downs -= 1
    question.feedback_ups += 1
    question.save()
    current_app.logger.info('[Down2Up][feedback_views]%s gave a down2up for question %s!'
                            % (current_user.name, q_dbid))
    return jsonify(errors.success())
