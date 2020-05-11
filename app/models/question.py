#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-11

from app import db


class QuestionModel(db.DynamicDocument):
    """
    正常使用的题目 question
    """
    text = db.StringField(max_length=40960)
    level = db.IntField(min_value=1, max_value=10)
    q_type = db.IntField(min_value=1, max_value=6)  # type是留字，可能会有一些坑，故使用q_type
    # 1 朗读 2 复述 3 问答 4 选择 5 短文本英文阅读 6 长文本英文阅读
    used_times = db.IntField(min_value=0, default=0)
    up_count = db.IntField(min_value=0, default=0)
    down_count = db.IntField(min_value=0, default=0)
    wordbase = db.DictField(default={})
    weights = db.DictField(default={})
    questions = db.ListField(default=None)  # 选择题集合可以包含若干选择题
    index = db.IntField(min_value=0)  # 题号，从0开始
    in_optimize = db.BooleanField(default=False)  # 现在是否在优化中
    last_optimize_time = db.DateTimeField(default=None)  # 最后优化时间
    auto_optimized = db.BooleanField(default=False)  # 是否被自动优化过
    feedback_ups = db.IntField(default=0)  # 短时重复切换状态时，请求可能不按顺序到达，可能短时间内<0
    feedback_downs = db.IntField(default=0)
    feedback_likes = db.IntField(default=0)

    meta = {'collection': 'questions'}

    def __str__(self):
        return "{id:%s,text:%s,level:%s,q_type:%s,used_times:%s,wordbase:%s}" % (
            self.id, self.text.__str__(), self.level.__str__(), self.q_type.__str__(), self.used_times.__str__(),
            self.wordbase.__str__())
