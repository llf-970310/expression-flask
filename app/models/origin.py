from app import db


class OriginTypeTwoQuestionModel(db.DynamicDocument):
    """
    正常使用的题目 question
    """
    text = db.StringField(max_length=512)
    wordbase = db.DictField(default={})
    q_id = db.IntField(min_value=0)  # 题号，从0开始
    origin = db.StringField(max_length=512)
    url = db.StringField(max_length=512)
    up_count = db.IntField(default=0)
    down_count = db.IntField(default=0)
    used_times = db.IntField(default=0)

    meta = {'collection': 'origin_questions'}

    def __str__(self):
        return "{id:%s,text:%s,level:%s,q_type:%s,used_times:%s,wordbase:%s}" % (
            self.id, self.text.__str__(), self.level.__str__(), self.q_type.__str__(), self.used_times.__str__(),
            self.wordbase.__str__())
