# -*- coding: utf-8 -*-
# Time       : 2019/3/17 17:18
# Author     : tangdaye
# Description: 邀请码
from app import db
import datetime


class InvitationModel(db.Document):
    code = db.StringField(max_length=64)
    creator = db.StringField(max_length=32)  # name
    available_times = db.IntField(min_value=0, default=1)
    vip_start_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    vip_end_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
    remaining_exam_num = db.IntField(min_value=0, default=0)
    remaining_exercise_num = db.IntField(min_value=0, default=0)
    activate_users = db.ListField(db.StringField(max_length=32))  # name
    create_time = db.DateTimeField(default=None)

    meta = {'collection': 'invitations', 'strict': False}

    def __str__(self):
        return 'code:%s\ncreator:%s\nvip_start_time:%s\nvip_end_time:%s\nremaining_exam_num:%d\nactivate_users:%s' \
               % (
                   self.code.__str__(), self.creator.__str__(), self.vip_start_time.__str__()[:19],
                   self.vip_end_time.__str__()[:19], self.remaining_exam_num, self.activate_users.__str__()
               )
