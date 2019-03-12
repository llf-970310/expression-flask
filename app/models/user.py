#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-20

from app import login_manager
from app import db
from flask_login import UserMixin
import datetime


@login_manager.user_loader
def load_user(user_id):
    return UserModel.objects(pk=user_id).first()


class Roles(object):
    Admin = 'admin'
    Default = 'default'


class UserModel(UserMixin, db.Document):
    # email = db.EmailField(max_length=128, required=True, unique=True)  # todo: enable
    # password = db.StringField(max_length=128, required=True)  # todo: enable
    email = db.EmailField(max_length=128)
    password = db.StringField(max_length=128)
    name = db.StringField(max_length=32, required=True)
    role = db.StringField(max_length=32, default=Roles.Default)
    register_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    last_login_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    questions_history = db.DictField(default={})  # {question_id: fetched_datetime, ...}
    student_id = db.StringField(max_length=32, unique=True)  # student_id should be unique. todo: remove?
    # birthday = db.DateTimeField()
    # gender = StringField(max_length=8)
    # wx_id = StringField(max_length=64)

    meta = {'collection': 'users', 'strict': False}

    def __repr__(self):
        return "{id:%s, email:%s, name:%s, role:%s}" % (self.id, self.email, self.name, self.role)

    def __str__(self):
        return "{id:%s,name:%s,student_id:%s,register_time:%s,last_login_time:%s}" % (
            self.id, self.name.__str__(), self.student_id.__str__(),
            self.register_time.__str__(), self.last_login_time.__str__())
