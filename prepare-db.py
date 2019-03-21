#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

from app.models.user import Roles, UserModel
from run_app import app

if __name__ == '__main__':
    admin = UserModel()
    admin.email = 'admin@site.com'
    admin.password = app.md5_hash('1234')
    admin.name = '管理员1'
    admin.role = Roles.Admin
    # admin.student_id = 'default'
    admin.save()
    print(type(admin.role))
    print(admin.role)
    print(admin.role == Roles.Default)
    print(admin.role == Roles.Admin)

    user1 = UserModel()
    user1.email = 'aaa@site.com'
    user1.password = app.md5_hash('1234')
    user1.name = '张三'
    user1.role = Roles.Default
    # user1.student_id = 'Mf1832144'
    user1.save()

    user2 = UserModel()
    user2.email = 'bbb@site.com'
    user2.password = app.md5_hash('1234')
    user2.name = '李四'
    user2.role = Roles.Default
    # user2.student_id = 'Mf1832110'
    user2.save()
