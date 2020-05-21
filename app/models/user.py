#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-20

from app import login_manager
from app import db
from app import errors
from flask_login import UserMixin
import datetime
from enum import Enum
from hashlib import md5

_MD5_SALT = 'a random string'  # 盐一旦使用后不可更改，否则历史数据会无效


@login_manager.user_loader
def load_user(user_id):
    return UserModel.objects(pk=user_id).first()


class Roles(Enum):
    Admin = 'admin'
    Default = 'user'


class UserModel(UserMixin, db.Document):
    # email = db.EmailField(max_length=128, required=True, unique=True)  # todo: enable
    # password = db.StringField(max_length=128, required=True)  # todo: enable
    email = db.EmailField(max_length=128)
    phone = db.StringField(max_length=16)
    __password = db.StringField(max_length=255, db_field='password')
    name = db.StringField(max_length=32, required=True)
    __role = db.StringField(max_length=32, default=Roles.Default.value)
    register_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    last_login_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    questions_history = db.DictField(default={})  # {question_id: fetched_datetime, ...}
    questions_liked = db.DictField(default={})  # {question_id: liked_datetime, ...}
    users_similar = db.DictField(default={})  # {user_id: similarity, ...}
    # student_id = db.StringField(max_length=32)  # student_id should be unique. todo: remove? should remove
    # university = db.StringField(max_length=32) # 改成枚举
    # college = db.StringField(max_length=32)
    # occupation = db.StringField(max_length=32) # 改成枚举
    # birthday = db.DateTimeField()
    # gender = db.StringField(max_length=8)
    wx_id = db.StringField(max_length=64, default='')
    vip_start_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    vip_end_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=1))
    remaining_exam_num = db.IntField(min_value=0, default=3)
    invitation_code = db.StringField(max_length=64, default='')

    meta = {'collection': 'users', 'strict': False}

    @property
    def role(self):
        return Roles(self.__role)

    @role.setter
    def role(self, Role):
        if isinstance(Role, Roles):
            self.__role = Role.value
        else:
            raise TypeError('Role must be a member of class Roles')

    def __repr__(self):
        return "{id:%s, email:%s, name:%s, role:%s}" % (self.id, self.email, self.name, self.role)

    def __str__(self):
        return "{id:%s,name:%s,register_time:%s,last_login_time:%s}" % (
            self.id, self.name.__str__(), self.register_time.__str__(), self.last_login_time.__str__())

    def is_admin(self):
        return self.__role == Roles.Admin.value

    def check_password(self, password: str):
        """验证密码（前后空格将被忽略）

        Args:
            password: 明文密码

        Returns:
            验证结果，True|False (bool)
        """
        password = password.strip()
        hash_obj = md5()
        hash_obj.update((password + _MD5_SALT).encode())
        return self.__password == hash_obj.hexdigest()

    def set_password(self, password: str):
        """设置hash后的密码但不保存，不要忘记手动保存！（前后空格将被忽略）

        Args:
            password: 明文密码

        Returns:
            None
        """
        password = password.strip()
        hash_obj = md5()
        hash_obj.update((password + _MD5_SALT).encode())
        self.__password = hash_obj.hexdigest()

    def can_do_exam(self):
        """验证是否有评测权限

        Returns:
            tuple: (status, error)
            status为True/False (Boolean)
            error为json格式错误信息（在app.errors中定义）
        """
        if self.remaining_exam_num <= 0:
            return False, errors.No_exam_times
        now = datetime.datetime.utcnow()
        if self.vip_end_time <= now:
            return False, errors.Vip_expired
        return True, None
