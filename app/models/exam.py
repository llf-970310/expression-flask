import datetime

from app import db


"""

参考资料：http://docs.mongoengine.org/guide/index.html , http://docs.mongoengine.org/apireference.html
中文资料：https://segmentfault.com/a/1190000008025156#articleHeader8

注意：
    1. 选取字段名称一定要慎重再慎重！！应该由良好的自解释性，不要引起歧义！！
    2. 合理拆分文件，不要一股脑把所有东西全写在一起！！（当然也不要胡乱拆分！）
    3. 最好保持类的属性名和数据库字段名一致，不用db_field指定，以便于理解使用

"""


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
    # status: "none|question_fetched|url_fetched|handling|finished",finished 由docker设置
    status = db.StringField(max_length=32, default="none")
    analysis_start_time = db.DateTimeField()
    feature = db.DictField(default={})
    score = db.DictField(default={})  # score field may has a set of scores
    analysis_end_time = db.DateTimeField()
    stack = db.StringField(max_length=1024)
    analysed = db.BooleanField()  # 这个回答是否被分析过

    # 默认没有get函数，手动添加支持
    def get(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return default


class CurrentTestModel(db.DynamicDocument):
    """
    current
    """
    user_id = db.StringField(max_length=32, default=None)
    openid = db.StringField(max_length=64, default=None)  # wx_christmas2019活动使用
    test_start_time = db.DateTimeField()
    test_expire_time = db.DateTimeField(default=datetime.datetime.utcnow())  # default只为兼容之前字段为空的情况
    paper_type = db.ListField()
    paper_tpl_id = db.StringField(max_length=24, default=None)
    current_q_num = db.IntField(min_value=1, default=1)
    score_info = db.DictField(default={})
    questions = db.DictField(default={})
    all_analysed = db.BooleanField()  # 这个考试中的所有回答是否都被分析过
    # make questions a dict rather than a list so as to be able update one question w/o affecting other questions

    meta = {'collection': 'current'}


class HistoryTestModel(db.DynamicDocument):
    """
    history
    TODO: 大部分内容和CurrentTestMode相同，是否可直接继承CurrentTestModel??
    """
    current_id = db.StringField(max_length=32, default=None)
    user_id = db.StringField(max_length=32, default=None)
    openid = db.StringField(default=None)
    test_start_time = db.DateTimeField()
    test_expire_time = db.DateTimeField()
    paper_type = db.ListField()
    paper_tpl_id = db.StringField(max_length=24, default=None)
    current_q_num = db.IntField(min_value=1, default=1)
    score_info = db.DictField(default={})
    questions = db.DictField(default={})
    all_analysed = db.BooleanField(default=False)  # 这个考试中的所有回答是否都被分析过

    meta = {'collection': 'history'}
