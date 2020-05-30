#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-10

from app.exam.exam_config import ExamConfig, QuestionConfig, DefaultValue
from flask import current_app

from app.models.cached.questions import get_cached_questions
from app.models.exam import *
from app.models.question import QuestionModel
from app.models.user import UserModel
from app.models.paper_template import PaperTemplate


class PaperUtils:
    @staticmethod
    def get_templates():
        all_templates = PaperTemplate.objects(deprecated=False)  # TODO: cache in redis
        tpl_lst = []
        for tpl in all_templates:
            d = {
                'tpl_id': str(tpl.id),
                'name': tpl.name,
                'desc': tpl.desc,
            }
            tpl_lst.append(d)
        return tpl_lst

    @staticmethod
    def init_paper(user, paper_tpl_id):
        paper_tpl = PaperTemplate.objects(id=paper_tpl_id).first()  # TODO: cache in redis
        if not paper_tpl:
            current_app.logger.error('[InitPaperError][init_paper]paper template not found:%s' % paper_tpl_id)
            return False
        current_test = CurrentTestModel()
        current_test.paper_tpl_id = paper_tpl_id
        current_test.user_id = str(user.id)
        _start_time = datetime.datetime.utcnow()
        current_test.test_start_time = _start_time
        current_test.test_expire_time = _start_time + datetime.timedelta(seconds=paper_tpl.duration)

        # 一次性取出全部试题（按使用次数倒序）
        # 选题条件：题号<=10000(大于10000的题目用作其他用途)
        d = {'index': {'$lte': 10000}}
        questions = QuestionModel.objects(__raw__=d).order_by('used_times')

        # 生成 paper_type 和 questions
        paper_type = []
        temp_all_q_lst = []
        q_chosen = set()  # 存放选中题目的id字符串
        use_backup = {}  # 避免每次选题都遍历数据库
        for q_needed in paper_tpl.questions:
            q_type = q_needed['q_type']
            q_id = q_needed['dbid']
            paper_type.append(q_type)  # 记入paper_type

            # 选题
            if isinstance(q_id, str) and len(q_id) in [24, 12]:  # 指定id
                q = QuestionModel.objects(id=q_id).first()
                temp_all_q_lst.append(q)
                q_chosen.add(q_id)
            else:  # 未指定id，按约定方案选题
                q_history = set(user.questions_history)
                q_backup_1 = None  # 记录已做过但未选中的指定类型题目,优先备选
                q_backup_2 = None  # 记录已选中的指定类型题目,最差的备选
                count_before = len(q_chosen)

                tactic = use_backup.get(q_type)
                if q_id == 0:  # 按最少使用次数选取指定类型的题目
                    # questions = get_cached_questions(q_type)  # TODO: 完善缓存处理机制
                    for q in questions:
                        if q.q_type != q_type:
                            continue
                        flag_add = False
                        qid_str = str(q.id)
                        if qid_str in q_chosen:
                            if tactic == 2:
                                flag_add = True
                            q_backup_2 = q if q_backup_2 is None else None
                        else:
                            if qid_str not in q_history:
                                flag_add = True
                            else:
                                if tactic == 1:
                                    flag_add = True
                                q_backup_1 = q if q_backup_1 is None else None
                        if flag_add:
                            temp_all_q_lst.append(q)
                            q_chosen.add(qid_str)
                            break
                # elif q_id == 1:  # 随机选取指定类型的题目
                #     pipeline = [{"$match": d}, {"$sample": {"size": 1}}]
                #     for _ in range(DefaultValue.max_random_try):
                #         rand_q = QuestionModel.objects.aggregate(*pipeline)
                #         qid_str = str(rand_q.id)
                #         if qid_str in q_chosen:
                #             q_backup_2 = rand_q if q_backup_2 is None else None
                #         else:
                #             if qid_str not in q_history:
                #                 temp_all_q_lst.append(rand_q)
                #                 q_chosen.add(qid_str)
                #                 break
                #             else:
                #                 q_backup_1 = rand_q if q_backup_1 is None else None
                # 如果题目数量不够，用重复的题目补够
                if len(q_chosen) == count_before:
                    if q_backup_1:
                        use_backup.update({q_type: 1})
                        temp_all_q_lst.append(q_backup_1)
                        q_chosen.add(str(q_backup_1.id))
                    else:  # 所有该类型题目不够组卷,使用相同题目组卷
                        if q_backup_2:
                            use_backup.update({q_type: 2})
                            temp_all_q_lst.append(q_backup_2)
                            q_chosen.add(str(q_backup_2.id))
                        else:  # 根本没有指定类型的题目
                            return False
        questions_chosen = {}
        for i in range(len(temp_all_q_lst)):  # TODO: 加缓存，异步刷入数据库?
            q = temp_all_q_lst[i]
            q_current = CurrentQuestionEmbed(q_id=str(q.id), q_type=q.q_type, q_text=q.text, wav_upload_url='')
            questions_chosen.update({str(i + 1): q_current})
            q.update(inc__used_times=1)  # 更新使用次数
        current_test.questions = questions_chosen
        current_test.paper_type = paper_type
        current_test.save()
        return str(current_test.id)

    @staticmethod
    def question_dealer(user_id: str, test, question_num: int) -> dict:
        user_id = str(user_id)
        # wrap question
        question = test.questions[str(question_num)]
        context = {"questionType": question.q_type,
                   "questionDbId": question.q_id,
                   "questionNumber": question_num,
                   "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
                   "lastQuestion": question_num == len(test.questions),
                   "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
                   "questionInfo": QuestionConfig.question_type_tip[question.q_type],
                   "questionContent": question.q_text,
                   "examLeftTime": (test.test_expire_time - datetime.datetime.utcnow()).total_seconds(),
                   "examTime": (test.test_expire_time - test.test_start_time).seconds
                   }

        # update and save
        # 这两个状态是否必要？？
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
