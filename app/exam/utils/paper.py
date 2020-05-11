#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-10

from app.exam.exam_config import ExamConfig, QuestionConfig
from flask import current_app
from app.models.exam import *
from app.models.question import QuestionModel
from app.models.user import UserModel
from app.models.paper_template import PaperTemplate


def compute_exam_score(score):
    # todo 这里暂时改成能用
    """
    计算考试成绩
    :param score: 考试各题成绩数组
    :return: 考试个维度成绩和总成绩
    """
    print(score)
    # for i in range(ExamConfig.total_question_num, 0, -1):
    #     if not score.get(i):
    #         print("in not")
    #         print(score.get(i))
    #         score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
    # print(score)

    total_quality = 0
    total_key = 0
    total_detail = 0
    total_structure = 0
    total_logic = 0
    for k, v in score.items():
        total_quality += v.get('quality', 0)
        total_key += v.get('key', 0)
        total_detail += v.get('detail', 0)
        total_structure += v.get('structure', 0)
        total_logic += v.get('logic', 0)

    x = {
        'quality': round(total_quality, 6),  # 1个题算平均?
        'key': round(total_key * 0.25, 6),  # 4个题算平均?
        'detail': round(total_detail * 0.25, 6),  # 4个题算平均?
        'structure': round(total_structure, 6),  # 1个题算平均?
        'logic': round(total_logic, 6)  # 1个题算平均?
    }
    x['total'] = round(x["quality"] * 0.3 + x["key"] * 0.35 + x["detail"] * 0.15 + x["structure"] * 0.1 + x[
        "logic"] * 0.1, 6)
    data = {"音质": x['quality'], "结构": x['structure'], "逻辑": x['logic'],
            "细节": x['detail'], "主旨": x['key'], "total": x['total']}
    print(data)
    return data


class PaperUtils:
    @staticmethod
    def init_paper(user, paper_tpl_id):
        paper_tpl = PaperTemplate.objects(id=paper_tpl_id).first()  # TODO: cache in redis
        if not paper_tpl:
            current_app.logger.error('[InitPaperError][init_paper]paper template not found:%s' % paper_tpl_id)
            return False
        current_test = CurrentTestModel()
        current_test.user_id = str(user.id)
        _start_time = datetime.datetime.utcnow()
        current_test.test_start_time = _start_time
        current_test.test_expire_time = _start_time + datetime.timedelta(seconds=paper_tpl.duration)

        current_test.questions = {}
        temp_all_q_lst = []
        for t in ExamConfig.question_num_each_type.keys():
            temp_q_lst = []
            question_num_needed = ExamConfig.question_num_each_type[t]
            if question_num_needed <= 0:
                continue
            d = {'q_type': t, 'index': {'$lte': 10000}}  # 题号<=10000, (大于10000的题目用作其他用途)

            questions = QuestionModel.objects(__raw__=d).order_by('used_times')  # 按使用次数倒序获得questions
            q_history = set(user.questions_history)
            q_backup = set()

            # do Not use repeated questions

            # # 方式一：随机选取
            # pipeline = [{"$match": d}, {"$sample": {"size": 1}}]
            # i = 0
            # while i < question_num_needed:
            #     rand_q = QuestionModel.objects.aggregate(*pipeline)
            #     the_q_id = str(rand_q.id)
            #     if the_q_id not in temp_q_lst:
            #         if the_q_id not in q_history:
            #             temp_q_lst.append(rand_q)
            #         else:
            #             q_backup.add(rand_q)
            #     if len(temp_q_lst) >= question_num_needed:
            #         break
            #     else:
            #         end = False
            #         if i // question_num_needed > 5:  # 要选n题，但选了5n次还不行，就用重复的
            #             for q in q_backup:
            #                 temp_q_lst.append(q)
            #                 if len(temp_q_lst) >= question_num_needed:
            #                     end = True
            #                     break
            #         if end:
            #             if len(temp_q_lst) < question_num_needed:  # 使用重复题目后数量还不够
            #                 return False
            #             break

            # 方式二：优先选使用次数少的
            for q in questions:
                if q.id.__str__() not in q_history:
                    temp_q_lst.append(q)
                else:
                    q_backup.add(q)
                if len(temp_q_lst) >= question_num_needed:
                    break
            # 如果题目数量不够，用重复的题目补够
            if len(temp_q_lst) < question_num_needed:
                for q in q_backup:
                    temp_q_lst.append(q)
                    if len(temp_q_lst) >= question_num_needed:
                        break

            # 如果题目数量不够，报错
            if len(temp_q_lst) < question_num_needed:
                current_app.logger.error("init_paper: Questions of Type %s Is Not Enough! "
                                         "need %s, but only has %s" % (t, question_num_needed, len(questions)))
                return False

            # 加入试题列表
            temp_all_q_lst += temp_q_lst

        for i in range(len(temp_all_q_lst)):
            q = temp_all_q_lst[i]
            q_current = CurrentQuestionEmbed(q_id=str(q.id), q_type=q.q_type, q_text=q.text, wav_upload_url='')
            current_test.questions.update({str(i + 1): q_current})
            q.update(inc__used_times=1)  # update

        # save
        current_test.save()
        return str(current_test.id)

    @staticmethod
    def question_dealer(question_num: int, test_id, user_id) -> dict:
        user_id = str(user_id)
        test_id = str(test_id)
        # get test
        test = CurrentTestModel.objects(id=test_id).first()
        if test is None:
            current_app.logger.error("question_generator ERROR: No Tests!, test_id: %s" % test_id)
            return {}

        # wrap question
        question = test.questions[str(question_num)]
        context = {"questionType": question.q_type,
                   "questionDbId": question.q_id,
                   "questionNumber": question_num,
                   "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
                   "lastQuestion": question_num == ExamConfig.total_question_num,
                   "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
                   "questionInfo": QuestionConfig.question_type_tip[question.q_type],
                   "questionContent": question.q_text,
                   "examLeftTime": (test.test_expire_time - datetime.datetime.utcnow()).total_seconds(),
                   "examTime": test.test_expire_time - test.test_start_time
                   }

        # update and save
        question.status = 'question_fetched'
        test.current_q_num = question_num
        test.save()

        # log question id to user's historical questions
        user = UserModel.objects(id=user_id).first()
        if user is None:
            current_app.logger.error("question_dealer: ERROR: user not find")
        user.questions_history.update({question.q_id: datetime.datetime.utcnow()})
        user.save()

        return context
