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


@questions.route('/<question_id>/like', methods=['POST'])
@login_required
def new_like(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    if str(question.id) in current_user.questions_liked:
        return jsonify(errors.success())

    question.feedback_likes += 1
    question.save()
    like_time = datetime.datetime.utcnow()
    current_user.questions_liked.update({question_id: like_time})
    current_user.save()
    current_app.logger.info('[NewLike][feedback_views]%s liked question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/like', methods=['DELETE'])
@login_required
def cancel_like(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    if str(question.id) not in current_user.questions_liked:
        return jsonify(errors.success())

    question.feedback_likes -= 1
    question.save()
    current_user.questions_liked.pop(question_id)
    current_user.save()
    current_app.logger.info('[LikeCanceled][feedback_views]%s canceled like for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/up', methods=['POST'])
@login_required
def new_up(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_ups += 1
    question.save()
    current_app.logger.info('[NewUp][feedback_views]%s gave an up for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/up', methods=['DELETE'])
@login_required
def cancel_up(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_ups -= 1
    question.save()
    current_app.logger.info('[UpCanceled][feedback_views]%s canceled an up for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/down', methods=['POST'])
@login_required
def new_down(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_downs += 1
    question.save()
    current_app.logger.info('[NewDown][feedback_views]%s gave a down for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/down', methods=['DELETE'])
@login_required
def cancel_down(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_downs -= 1
    question.save()
    current_app.logger.info('[DownCanceled][feedback_views]%s canceled a down for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/up2down', methods=['POST'])
@login_required
def up2down(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_ups -= 1
    question.feedback_downs += 1
    question.save()
    current_app.logger.info('[Up2Down][feedback_views]%s gave an up2down for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())


@questions.route('/<question_id>/down2up', methods=['POST'])
@login_required
def down2up(question_id):
    question, err = get_question_obj(question_id)
    if err:
        return jsonify(err)
    question.feedback_downs -= 1
    question.feedback_ups += 1
    question.save()
    current_app.logger.info('[Down2Up][feedback_views]%s gave a down2up for question %s!'
                            % (current_user.name, question_id))
    return jsonify(errors.success())
