#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-03-08

from app.models.question import QuestionModel
from app import errors
from flask import current_app


def get_question_obj(question_id):
    """
    获取question对象
    :param question_id: 题目的 _id
    :return: (question, err_dict)
    """
    try:
        question = QuestionModel.objects(id=question_id).first()
        if question is None:
            return None, errors.Question_not_exist
        return question, None
    except Exception as e:
        current_app.logger.error('[Exception][feedback.utils]cannot get question:%s\n\t%s'
                                 % (question_id, str(e)))
        return None, errors.exception({'msg': str(e)})
