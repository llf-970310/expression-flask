#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-03-08

from app.models.exam import QuestionModel
from app import errors
from flask import current_app


def get_question_obj(q_dbid):
    """
    获取question对象
    :param q_dbid:
    :return: (question, err_dict)
    """
    try:
        question = QuestionModel.objects(id=q_dbid).first()
        if question is None:
            return None, errors.Question_not_exist
        return question, None
    except Exception as e:
        current_app.logger.error('[Exception][feedback.utils]cannot get question:%s\n\t%s'
                                 % (q_dbid, str(e)))
        return None, errors.exception({'msg': str(e)})
