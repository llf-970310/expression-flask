#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-07

from __future__ import absolute_import
import datetime
from app import db


class ApJob(db.DynamicDocument):
    meta = {'collection': 'jobs'}
    _id = db.StringField(max_length=64, required=True)
    next_run_time = db.FloatField()
    job_state = db.BinaryField()

    def get_id(self):
        return self._id


class ApJobBackup(db.DynamicDocument):
    """
    apscheduler定时任务Model
    """
    meta = {'collection': 'apscheduler'}
    name = db.StringField(max_length=32, unique=True, required=True)
    annotation = db.StringField(max_length=512, default='')
    create_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    job = db.DictField(default={})
