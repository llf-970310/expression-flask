import datetime

from app import db


# 参考资料：http://docs.mongoengine.org/guide/index.html , http://docs.mongoengine.org/apireference.html
# 中文资料：https://segmentfault.com/a/1190000008025156#articleHeader8


class WavPretestModel(db.DynamicDocument):
    """
    用户的音频测试 wav+test
    """
    text = db.StringField(max_length=512)
    user_id = db.StringField(max_length=32)
    test_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    file_location = db.StringField(max_length=32, default='local')
    wav_upload_url = db.StringField(max_length=256)
    result = db.DictField(default={'status': 'none', 'feature': {}})
    meta = {'collection': 'wav_test'}


class QuestionModel(db.DynamicDocument):
    """
    正常使用的题目 question
    """
    text = db.StringField(max_length=512)
    level = db.IntField(min_value=1, max_value=10)
    q_type = db.IntField(min_value=1, max_value=3)  # type是留字，可能会有一些坑
    used_times = db.IntField(min_value=0, default=0)
    up_count = db.IntField(min_value=0, default=0)
    down_count = db.IntField(min_value=0, default=0)
    wordbase = db.DictField(default={})
    weights = db.DictField(default={})
    questions = db.ListField(default=None)  # 选择题集合可以包含若干选择题
    q_id = db.IntField(min_value=0)  # 题号，从0开始
    in_optimize = db.BooleanField(default=False)  # 现在是否在优化中
    last_optimize_time = db.DateTimeField(default=None)  # 最后优化时间
    auto_optimized = db.BooleanField(default=False)  # 是否被自动优化过

    meta = {'collection': 'questions'}

    def __str__(self):
        return "{id:%s,text:%s,level:%s,q_type:%s,used_times:%s,wordbase:%s}" % (
            self.id, self.text.__str__(), self.level.__str__(), self.q_type.__str__(), self.used_times.__str__(),
            self.wordbase.__str__())


class CurrentQuestionEmbed(db.EmbeddedDocument):
    """
    用户做题的题目 current.question[x]
    """
    q_id = db.StringField(max_length=32)
    q_type = db.IntField(min_value=1, max_value=3)
    q_text = db.StringField(max_length=512)
    file_location = db.StringField(max_length=32)
    wav_upload_url = db.StringField(max_length=256)
    wav_temp_url = db.StringField(max_length=256)
    status = db.StringField(max_length=32,
                            default="none")  # "none|url_fetched|handling|finished",finished 由docker设置
    analysis_start_time = db.DateTimeField()
    feature = db.DictField(default={})
    score = db.DictField(default={})  # score field may has a set of scores
    analysis_end_time = db.DateTimeField()
    stack = db.StringField(max_length=1024)
    analysed = db.BooleanField()  # 这个回答是否被分析过


class CurrentTestModel(db.DynamicDocument):
    """
    current
    """
    user_id = db.StringField(max_length=32, default=None)
    openid = db.StringField(max_length=64, default=None)  # wx_christmas2019活动使用
    test_start_time = db.DateTimeField()
    paper_type = db.ListField()
    current_q_num = db.IntField(min_value=1, default=1)
    score_info = db.DictField(default={})
    questions = db.DictField(default={})
    all_analysed = db.BooleanField()  # 这个考试中的所有回答是否都被分析过
    # make questions a dict rather than a list so as to be able update one question w/o affecting other questions

    meta = {'collection': 'current'}


class HistoryTestModel(db.DynamicDocument):
    """
    history
    """
    current_id = db.StringField(max_length=32, default=None)
    user_id = db.StringField(max_length=32, default=None)
    openid = db.StringField(default=None)
    test_start_time = db.DateTimeField()
    paper_type = db.ListField()
    current_q_num = db.IntField(min_value=1, default=1)
    score_info = db.DictField(default={})
    questions = db.DictField(default={})
    all_analysed = db.BooleanField(default=False)  # 这个考试中的所有回答是否都被分析过

    meta = {'collection': 'history'}


class CurrentStatisticsModel(db.Document):
    meta = {'collection': 'current_stat'}
    stat_time = db.DateTimeField(default=lambda: datetime.datetime.utcnow())
    total_cnt = db.IntField(default=0)
    user_test_cnt = db.IntField(default=0)
    batch_test_cnt = db.IntField(default=0)
