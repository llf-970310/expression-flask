# coding: utf-8
import datetime
import time

from flask import current_app

from app.models.exam import CurrentTestModel, QuestionModel, CurrentQuestionEmbed
from app.models.user import UserModel
from .exam_config import ExamConfig, QuestionConfig
from app_config import redis_client


def compute_exam_score(score):
    """
    计算考试成绩
    :param score: 考试各题成绩数组
    :return: 考试个维度成绩和总成绩
    """
    print(score)
    for i in range(ExamConfig.total_question_num, 0, -1):
        if not score.get(i):
            print("in not")
            print(score.get(i))
            score[i] = {"quality": 0, "key": 0, "detail": 0, "structure": 0, "logic": 0}
    print(score)
    x = {
        "quality": round(score[1]['quality'], 6),
        "key": round(score[2]['key'] * 0.25 + score[3]['key'] * 0.25 + score[4]['key'] * 0.25 + score[5][
            'key'] * 0.25, 6),
        "detail": round(score[2]['detail'] * 0.25 + score[3]['detail'] * 0.25 + score[4]['detail'] * 0.25 +
                        score[5]['detail'] * 0.25, 6),
        "structure": round(score[6]['structure'], 6),
        "logic": round(score[6]['logic'], 6)
    }
    x['total'] = round(x["quality"] * 0.3 + x["key"] * 0.35 + x["detail"] * 0.15 + x["structure"] * 0.1 + x[
        "logic"] * 0.1, 6)
    data = {"音质": x['quality'], "结构": x['structure'], "逻辑": x['logic'],
            "细节": x['detail'], "主旨": x['key'], "total": x['total']}
    print(data)
    return data


def get_server_date_str(separator='') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    return time.strftime("%%Y%s%%m%s%%d" % (separator, separator), time.localtime(time.time()))


class ExamSession:
    @staticmethod
    def set(user_id, name, value, ex=int(ExamConfig.exam_total_time), px=None, nx=False, xx=False):
        user_id = str(user_id)
        key = 'ES##%s##%s' % (user_id, name)
        return redis_client.set(key, value, ex, px, nx, xx)

    @staticmethod
    def get(user_id, name, default=None):
        user_id = str(user_id)
        key = 'ES##%s##%s' % (user_id, name)
        ret = redis_client.get(key)
        return ret.decode() if ret is not None else default

    @staticmethod
    def expire(user_id, name, time):
        user_id = str(user_id)
        key = 'ES##%s##%s' % (user_id, name)
        return redis_client.expire(key, time)


class QuestionUtils:
    @staticmethod
    def init_question(user):
        current_test = CurrentTestModel()
        current_test.user_id = str(user.id)
        current_test.test_start_time = datetime.datetime.utcnow()

        current_test.questions = {}
        temp_all_q_lst = []
        for t in ExamConfig.question_num_each_type.keys():
            temp_q_lst = []
            question_num_needed = ExamConfig.question_num_each_type[t]
            d = {'q_type': t, 'q_id': {'$lte': 10000}}  # 题号<=10000, (大于10000的题目用作其他用途)

            questions = QuestionModel.objects(__raw__=d).order_by('used_times')  # 按使用次数倒序获得questions
            if ExamConfig.question_allow_repeat[t]:
                for q in questions:
                    temp_q_lst.append(q)
                    if len(temp_q_lst) >= question_num_needed:
                        break
            else:  # do Not use repeated questions
                q_history = set(user.questions_history)
                q_backup = set()

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
                    current_app.logger.error("init_question: Questions of Type %s Is Not Enough! "
                                             "need %s, but only has %s" % (t, question_num_needed, len(questions)))
                    return False

            # 加入试题列表
            temp_all_q_lst += temp_q_lst

        for i in range(len(temp_all_q_lst)):
            q = temp_all_q_lst[i]
            q_current = CurrentQuestionEmbed(q_dbid=str(q.id), q_type=q.q_type, q_text=q.text, wav_upload_url='')
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
                   "questionDbId": question.q_dbid,
                   "questionNumber": question_num,
                   "questionLimitTime": ExamConfig.question_limit_time[question.q_type],
                   "lastQuestion": question_num == ExamConfig.total_question_num,
                   "readLimitTime": ExamConfig.question_prepare_time[question.q_type],
                   "questionInfo": QuestionConfig.question_type_tip[question.q_type],
                   "questionContent": question.q_text,
                   "examLeftTime": ExamConfig.exam_total_time - (datetime.datetime.utcnow() - test[
                       'test_start_time']).total_seconds(),
                   "examTime": ExamConfig.exam_total_time
                   }

        # update and save
        question.status = 'question_fetched'
        test.current_q_num = question_num
        test.save()

        # log question id to user's historical questions
        user = UserModel.objects(id=user_id).first()
        if user is None:
            current_app.logger.error("question_dealer: ERROR: user not find")
        user.questions_history.update({question.q_dbid: datetime.datetime.utcnow()})
        user.save()

        return context


if __name__ == '__main__':
    pass
    # x = {
    #     "name": "褚东宇"
    # }
    # path = save_dict_to_path(x, name='1234.json', dir='/Users/tangdaye/ttt/ttt/')
    # dic = get_dict_from_path(path)
