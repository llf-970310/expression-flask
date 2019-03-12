import datetime

from app import db
from mongoengine import *


# 参考资料：http://docs.mongoengine.org/guide/index.html , http://docs.mongoengine.org/apireference.html
# 中文资料：https://segmentfault.com/a/1190000008025156#articleHeader8


class UserModel(Document):
    name = StringField(max_length=32)
    student_id = StringField(max_length=32, unique=True)  # student_id should be unique
    register_time = DateTimeField(default=lambda: datetime.datetime.utcnow())
    last_login_time = DateTimeField(default=lambda: datetime.datetime.utcnow())
    questions_history = DictField(default={})  # {question_id: fetched_datetime, ...}
    password = StringField(max_length=32)

    meta = {'collection': 'users'}

    # wx_id = StringField()
    # age = IntField(min_value=0)
    # gender = StringField(max_length=8)
    # job = StringField(max_length=32)
    # last_test_id = StringField()

    def __str__(self):
        return "{id:%s,name:%s,student_id:%s,register_time:%s,last_login_time:%s}" % (
            self.id, self.name.__str__(), self.student_id.__str__(),
            self.register_time.__str__(), self.last_login_time.__str__())


class QuestionModel(db.DynamicDocument):
    text = db.StringField(max_length=512)
    level = db.IntField(min_value=1, max_value=10)
    q_type = db.IntField(min_value=1, max_value=3)  # type是留字，可能会有一些坑
    used_times = db.IntField(min_value=0, default=0)
    wordbase = db.DictField(default={})

    meta = {'collection': 'questions'}

    def __str__(self):
        return "{id:%s,text:%s,level:%s,q_type:%s,used_times:%s,wordbase:%s}" % (
            self.id, self.text.__str__(), self.level.__str__(), self.q_type.__str__(), self.used_times.__str__(),
            self.wordbase.__str__())


class CurrentQuestionEmbed(db.EmbeddedDocument):
    q_id = db.StringField(max_length=32)
    q_type = db.IntField(min_value=1, max_value=3)
    q_text = db.StringField(max_length=512)
    wav_upload_url = db.StringField(max_length=256)
    wav_temp_url = db.StringField(max_length=256)
    status = db.StringField(max_length=32,
                            default="none")  # "none|url_fetched|handling|finished",finished 由docker设置
    analysis_start_time = db.DateTimeField()
    feature = db.DictField(default={})
    score = db.DictField(default={})  # score field may has a set of scores
    analysis_end_time = db.DateTimeField()
    stack = db.StringField(max_length=1024)


class CurrentTestModel(db.Document):
    user_id = db.StringField(max_length=32)
    test_start_time = db.DateTimeField()
    paper_type = db.ListField()
    current_q_num = db.IntField(min_value=1, default=1)
    total_score = db.FloatField(min_value=0.0, max_value=100.0, default=0.0)
    questions = db.DictField(default={})
    # make questions a dict rather than a list so as to be able update one question w/o affecting other questions

    meta = {'collection': 'current'}


class ApiAccountModel(db.DynamicDocument):
    meta = {'collection': 'api_accounts'}
    type = db.StringField(max_length=32)
    accounts = db.ListField()
