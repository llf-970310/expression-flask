#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-11

import datetime
from app import db


class CurrentStatisticsModel(db.Document):
    meta = {'collection': 'current_stat'}
    stat_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    total_cnt = db.IntField(default=0)
    user_test_cnt = db.IntField(default=0)
    batch_test_cnt = db.IntField(default=0)
