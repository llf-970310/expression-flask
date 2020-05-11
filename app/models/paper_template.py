#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-10

from app import db

"""
...
questions: [
    {type: int, dbid: ObjectId or 0},
    {type: int, dbid: ObjectId or 0}
]
"""

# TODO: 创建考试时使用paper template，并且直接算出并加上expire时间，不在需要根据超时时间计算


class PaperTemplate(db.Document):

    meta = {'collection': 'paper_tpl'}

    deprecated = db.BooleanField(default=False)  # 是否废弃不用
    need_auth = db.BooleanField(default=False)
    password = db.StringField(max_length=128, default=None)
    duration = db.IntField(min=1, default=1800)  # 考试时长,seconds

    name = db.StringField(max_length=128, required=True)
    desc = db.StringField(max_length=512, default=None)
    questions = db.ListField(required=True)

    def total_question_num(self):
        return len(self.questions)


# def init_db():
#     paper_tpl = PaperTemplate()
#     paper_tpl.time_limit = 1800
#     paper_tpl.name = '含英语题目的表达能力测试'
#     paper_tpl.questions = [
#         {'q_type': 1, 'dbid': 0},
#         {'q_type': 3, 'dbid': 0},
#         {'q_type': 5, 'dbid': 0},
#         {'q_type': 5, 'dbid': 0},
#         {'q_type': 6, 'dbid': 0},
#         {'q_type': 6, 'dbid': 0}
#     ]
#     paper_tpl.save()
#
#     paper_tpl = PaperTemplate()
#     paper_tpl.time_limit = 1800
#     paper_tpl.name = '原始表达能力测试'
#     paper_tpl.questions = [
#         {'q_type': 1, 'dbid': 0},
#         {'q_type': 2, 'dbid': 0},
#         {'q_type': 2, 'dbid': 0},
#         {'q_type': 2, 'dbid': 0},
#         {'q_type': 2, 'dbid': 0},
#         {'q_type': 3, 'dbid': 0}
#     ]
#     paper_tpl.save()
#
#     paper_tpl = PaperTemplate()
#     paper_tpl.time_limit = 1800
#     paper_tpl.name = '2019圣诞小程序测试'
#     paper_tpl.questions = [
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 4, 'dbid': 1},
#         {'q_type': 1, 'dbid': 1},
#         {'q_type': 3, 'dbid': 1}
#     ]
#     paper_tpl.save()


if __name__ == '__main__':
    from mongoengine import connect
    from app_config import MongoConfig

    connect(MongoConfig.db, host=MongoConfig.host, port=MongoConfig.port,
            username=MongoConfig.user, password=MongoConfig.password, authentication_source=MongoConfig.db,
            authentication_mechanism=MongoConfig.auth)

