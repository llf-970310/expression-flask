import datetime

from app import db

class OriginQuestionModel(db.DynamicDocument):
    """
    正常使用的题目 question
    """
    q_type = db.IntField(min_value=1, max_value=3)  # type是留字，可能会有一些坑
    level = db.IntField(min_value=1, max_value=10)
    text = db.StringField(max_length=512)
    wordbase = db.DictField(default={})
    q_id = db.IntField(min_value=0)  # 题号，从0开始

    meta = {'collection': 'origin_questions'}

    def __str__(self):
        return "{id:%s,text:%s,level:%s,q_type:%s,used_times:%s,wordbase:%s}" % (
            self.id, self.text.__str__(), self.level.__str__(), self.q_type.__str__(), self.used_times.__str__(),
            self.wordbase.__str__())
