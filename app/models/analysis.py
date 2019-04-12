import datetime

from app import db


class AnalysisModel(db.DynamicDocument):
    question_num = db.IntField(min_value=0, default=-1)
    exam_id = db.StringField(max_length=32)
    question_id = db.StringField(max_length=32)
    score_detail = db.FloatField(default=0, min_value=0)
    score_key = db.FloatField(default=0, min_value=0)
    voice_features = db.DictField(default={})
    key_hits = db.ListField(db.FloatField(default=0))
    detail_hits = db.ListField(db.ListField(db.FloatField(default=0)))
    user = db.ObjectIdField()
    date = db.DateTimeField()

    meta = {'collection': 'analysis'}


class OptimizeModel(db.DynamicDocument):
    question_num = db.IntField(min_value=0, default=-1)
    wordbase = db.DictField(default={})
    weights = db.DictField(default={})
    key_history_cost = db.ListField(db.FloatField(default=0))
    detail_history_cost = db.ListField(db.FloatField(default=0))
    complete_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    finish = db.BooleanField(default=True)
    meta = {'collection': 'optimize'}
