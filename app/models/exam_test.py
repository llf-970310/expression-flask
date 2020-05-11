#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7

from app.models.exam import *
from app.models.question import QuestionModel
from app.models.user import UserModel

import time
import datetime
from mongoengine import connect

MONGODB = {
    'NAME': 'expression',
    'HOST': 'mongo-server.expression.hosts',
    'PORT': 27017,  # caution: integer here (unlike django default)
    'NEED_AUTH': True,
    'AUTH_MECHANISM': 'SCRAM-SHA-1',
    'USER': 'iselab',
    'PASSWORD': 'iselab###nju.cn'
}
connect(MONGODB['NAME'], host=MONGODB['HOST'], port=MONGODB['PORT'],
        username=MONGODB['USER'], password=MONGODB['PASSWORD'], authentication_source=MONGODB['NAME'],
        authentication_mechanism=MONGODB['AUTH_MECHANISM'])

# connect('expression_test', host='127.0.0.1', port=27017)


def history_test():
    histories = HistoryTestModel.objects()
    print(len(histories))
    for history in histories:
        history['all_analysed'] = False
        history.save()


def question_type4_test():
    q = QuestionModel.objects(index=10001).first()
    print(q)
    print(q.questions)


if __name__ == '__main__':
    pass
    question_type4_test()

    # ---------------------------example:add(simple)-------------------------------------------
    # question = QuestionModel()
    # question.text = '工作时间之外，是否应该接听工作电话，处理工作？请你谈谈对这个问题的看法。'
    # question.q_type = 3
    # question.level = 1
    # # question.used_times = 0这是默认的，不用写出
    # question.save()
    #
    # question2 = QuestionModel()
    # question2.text = "高铁是现在是最受欢迎的出行方式，首先，高铁速度快，比如说，以前从贵阳到北京，要用40个小时左右，但现在高铁只需要6个小时，" \
    #                  "大大减少了路途时间。其次，高铁正点率高，因为高铁受天气条件影响较小，通常都可以准时发车，按时到达。最后，高铁环境舒适，" \
    #                  "高铁坐席宽敞，运行时速度平稳，没有噪音，餐车环境整洁，配有电源插座和无线网络，乘坐高铁很少会造成不适感，" \
    #                  "对于不习惯坐飞机出行的人士，高铁是更理想的选择。但高铁的建设，前期投资非常巨大，对设备技术、制作工艺要求都很高，" \
    #                  "后期的管理运营也需要更专业的人员来完成。(2)"
    # question2.q_type = 2
    # question2.level = 1
    # # question.used_times = 0这是默认的，不用写出
    # question2.wordbase = {
    #     "key": [],
    #     "detail": [],
    # }
    # question2.save()
    #
    # # ---------------------------example:add(complicate)-------------------------------------------
    # current_test = CurrentTestModel()
    # # users = UserModel.objects(student_id="MF1832144")
    # # current_test.user_id = users[0].id.__str__()
    # # current_test.test_start_time = datetime.datetime.strptime('2018-11-11 00:08:00', '%Y-%m-%d %H:%M:%S')
    # # current_test.paper_type = [1, 1, 0]
    # # current_test.current_q_num = 1 这个是默认的，生成的时候不用写
    # # current_test.total_score=0.0这个是默认的，生成的时候不用写
    # q1 = QuestionModel.objects[0]
    # q1_current = CurrentQuestionEmbed(q_id=q1.id.__str__(), q_type=q1.q_type, q_text=q1.text,
    #                                   wav_upload_url="default wav upload url", wav_temp_url="default wav temp url")
    # # q1_current.status="none"这个是默认的，生成的时候不用写
    # q2 = QuestionModel.objects[1]
    # q2_current = CurrentQuestionEmbed(q_id=q2.id.__str__(), q_type=q2.q_type, q_text=q2.text,
    #                                   wav_upload_url="default wav upload url", wav_temp_url="default wav temp url")
    # # q2_current.status="none"这个是默认的，生成的时候不用写
    # current_test.questions.update({"%s" % 1: q1_current})
    # current_test.questions.update({"%s" % 2: q2_current})
    # # current_test.questions["%s" % 1] = q1_current
    # # current_test.questions["%s" % 2] = q2_current
    # current_test.save()
    #
    # questions = QuestionModel.objects.order_by('-used_times')  # 按照使用次数倒序排列（使用次数最多的在前面）
    # for question in questions:
    #     print(question)
    #
    # # ---------------------------------------example:update-------------------------------------------
    # update_item_count1 = QuestionModel.objects.update(
    #     inc__used_times=1)  # 将所有的question的使用次数加1，inc表示加,这个方法的返回值是影响的条目数
    # current = CurrentTestModel.objects[0]  # 先获得某次考试
    # q = current.questions[0]  # 获得它的某道题
    # q.status = 'url_fetched'  # 修改这道题的状态
    # update_item_count2 = current.update(set__questions__0=q)  # set表示设置，0是下标，和前面的current.questions[0]要对应
    # # 更新第一次考试的第一题的状态，设置成url_fetched
