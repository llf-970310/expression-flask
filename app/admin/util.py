# -*- coding: utf-8 -*-
# Time       : 2019/3/18 11:43
# Author     : tangdaye
# Description: admin util
import abc
import time
from functools import reduce

from app.admin.admin_config import PaginationConfig, ScoreConfig
from flask import current_app

from app.admin.algorithm import OptimizeAlgorithm

from app.models.exam import QuestionModel

from app.utils.profiler import func_time, func_cprofile

al_num = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def generate_random_code(length=4):
    import random
    s = ''
    for i in range(length):
        s += random.choice(al_num)
    return s


def convert_date_to_str(date, separator='-') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    return date.strftime("%%Y%s%%m%s%%d" % (separator, separator))


def convert_datetime_to_str(utc_time, date_separator='-') -> str:
    """
    Desc:   获得当前日期格式化字符串，可指定分隔符，如: 20181009(默认), 2018-10-31(输入为-), 2018===10===31(输入为===)
    """
    if not utc_time:
        return ''
    return utc_time.strftime("%%Y%s%%m%s%%d %%H:%%M:%%S" % (date_separator, date_separator))


def str_to_bool(str):
    return True if str.lower() == 'true' else False


def array2str(array, level):
    """

    :param array: 需要展示的的原数组
    :param level: 数组需要遍历的层级
    :return: 可直接展示的 word 的数组
    """
    if level == 1:
        string = "「"
        split = '，'
        string += split.join(array)
        string += "」"
    elif level == 2:
        string = "「"
        for i in range(0, len(array)):
            split = '，'
            string += ('「' + split.join(array[i]) + '」')
            if i < len(array) - 1:
                string += '，'
        string += '」'
    elif level == 3:
        string = '「'
        for i in range(0, len(array)):
            string += "「"
            for j in range(0, len(array[i])):
                split = '，'
                string += ('「' + split.join(array[i][j]) + '」')
                if j < len(array[i]) - 1:
                    string += '，'
            string += '」'
            if i < len(array) - 1:
                string += '，'
        string += '」'
    else:
        string = ''
    return string


# views_question
def get_page_and_size_from_request_args(args):
    """从请求中获得参数

    :param args: request.args get请求的参数
    :return: get请求中的page、size参数组成的元组
    """
    page = args.get('page')
    size = args.get('size')

    # 参数小于0不合法，日志记录
    if page and int(page) < 0:
        current_app.logger.info('page is not applicable, and page = %d', page)
    if size and int(size) < 0:
        current_app.logger.info('size is not applicable, and size = %d', size)

    # 提供默认参数
    if page is None or page == '' or int(page) < 0:
        page = PaginationConfig.DEFAULT_PAGE
    else:
        page = int(page)

    if size is None or size == '' or int(size) < 0:
        size = PaginationConfig.DEFAULT_SIZE
    else:
        size = int(size)

    current_app.logger.info('page = %d, size = %d', page, size)
    return page, size


def get_next_available_question_id():
    """获取当前题目 question 中最大的题号

    :return: 当前最大题号
    """
    max_question = QuestionModel.objects().order_by('-q_id').limit(1).first()
    return max_question['q_id'] + 1


def reset_question_weights(wordbase):
    """
    1。 重置问题关键词的权重：权重的数量等于词的数量加一，每个词的权重=100/权重的数量
    2。 重置权重的击中次数为0
    """
    weights = {}
    len_keywords = len(wordbase['keywords'])
    len_detailwords = len(reduce(lambda x, y: x + y, wordbase['detailwords']))

    # 重置问题关键词的权重
    key_init = 100 / (len_keywords + 1)
    detail_init = 100 / (len_detailwords + 1)
    weights['key'] = [key_init for i in range(len_keywords + 1)]
    weights['detail'] = [detail_init for i in range(len_detailwords + 1)]

    # 重置权重的击中次数为0
    weights['key_hit_times'] = [0 for i in range(len_keywords)]
    weights['detail_hit_times'] = [0 for i in range(len_detailwords)]
    return weights


# views_score
class AbstractMapper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def map_answers(self, answers):
        """
        将回答 list 按照一定规则对应为 dict
        """
        return


class QuestionNumMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照题号对应

        :param answers: 所有的回答
        :return: key 为题号，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_question_id = answer['question_num']
            if cur_question_id in res:
                res[cur_question_id].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_question_id] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


class UserMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照用户对应

        :param answers: 所有的回答
        :return: key 为用户 ObjectId，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_user = answer['user']
            if cur_user in res:
                res[cur_user].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_user] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


class DateMapper(AbstractMapper):

    def map_answers(self, answers):
        """将所有回答结果按照回答日期对应

            :param answers: 所有的回答
            :return: key 为日期，value 为相应的 {key, detail} 得分的字典
        """
        res = {}
        for answer in answers:
            cur_date = convert_date_to_str(answer['test_start_time'])
            if cur_date in res:
                res[cur_date].append({'key': answer['score_key'], 'detail': answer['score_detail']})
            else:
                res[cur_date] = [{'key': answer['score_key'], 'detail': answer['score_detail']}]
        return res


def generate_result_from_dict(dict, result_key_name):
    """

    :param dict: {result_key: {key, detail}]}
    :param result_key_name: 结果集中的 key 值
    :return:
    """
    from app.exam.exam_config import ExamConfig
    algorithm = OptimizeAlgorithm()

    result = []
    for key in dict:
        cur_answers = dict[key]
        detail_scores = [cur_answer['detail'] for cur_answer in cur_answers]
        key_scores = [cur_answer['key'] for cur_answer in cur_answers]

        key_score = algorithm.analysis_score(key_scores, ExamConfig.full_score)['mean']
        detail_score = algorithm.analysis_score(detail_scores, ExamConfig.full_score)['mean']
        result.append({
            result_key_name: key,
            'times': len(cur_answers),
            'mainScore': format(key_score, ScoreConfig.DEFAULT_NUM_FORMAT),
            'detailScore': format(detail_score, ScoreConfig.DEFAULT_NUM_FORMAT),
            'totalScore': generate_total_score(key_score, detail_score)
        })
    return result


def sort_by_question_id(array_item):
    return array_item['questionId']


def generate_total_score(key_score, detail_score):
    from app.exam.exam_config import ExamConfig
    return format(key_score * ExamConfig.key_percent + detail_score * ExamConfig.detail_percent,
                  ScoreConfig.DEFAULT_NUM_FORMAT)


# views_optimize
def question2weight(question):
    detail = []
    for lst in question['wordbase']['detailwords']:
        detail += lst
    res = {
        'keyWords': question['wordbase']['keywords'],
        'keyWeight': question['weights']['key'],
        'keyHitTimes': question['weights']['key_hit_times'],
        'detailWords': detail,
        'detailWeight': question['weights']['detail'],
        'detailHitTimes': question['weights']['detail_hit_times']
    }
    return res