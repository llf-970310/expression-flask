#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7
import os


class PathConfig(object):
    parent_abs_path = '/expression'
    audio_save_basedir = 'audio'
    audio_copy_temp_basedir = 'temp_audio'
    audio_test_basedir = 'audio/test'
    audio_extension = '.wav'


class ExamConfig(object):
    question_limit_time = {0: 15, 1: 60, 2: 30, 3: 120, 4: 0, 5: 60, 6: 120, 7: 120}
    question_prepare_time = {0: 5, 1: 5, 2: 60, 3: 60, 4: 0, 5: 120, 6: 240, 7: 120}
    detect_left_exam = True  # 是否断点续作

    # TODO: 下面参数在定时优化代码中使用,代码需要检查，可能需要重写
    key_percent = 0.7
    detail_percent = 0.3
    full_score = 100


class QuestionConfig(object):
    question_type_tip = {
        1: {"detail": "声音质量测试。点击 “准备作答” 按钮后请先熟悉屏幕上的文字，然后按下 “开始录音” 按钮朗读该段文字。"
                      "<br><br>该题作答完毕后，请按下“提前结束”按钮停止录音。",
            "tip": '为了保证测试准确性，请选择安静环境，并对准麦克风。'},
        2: {"detail": "点击 “准备作答” 后，请先阅读屏幕上的文字。之后，请在规定时间内尽可能完整地讲述段落大意及细节信息。",
            "tip": '约350字，阅读时间一分钟，讲述时间30秒。'},
        3: {"detail": "根据问题发表自己观点。", "tip": "准备1分钟 叙述2分钟"},
        4: {},
        5: {"detail": "点击 “准备作答” 后，你将看到一篇英文短文，一段时间准备后，请用<strong>中文</strong>复述文章。",
            "tip": "你有2分钟的时间准备，并有1分钟时间复述"},
        6: {"detail": "点击 “准备作答” 后，你将看到一篇英文长文，一段时间准备后，请用<strong>中文</strong>复述文章。",
            "tip": "你有4分钟的时间准备，并有2分钟时间复述"},
        7: {"detail": "点击 “准备作答” 后，你将看到一个技术问答题，一段时间准备后，请用中文作答。",
            "tip": "你有2分钟的时间准备，并有2分钟时间复述"}
    }
    pretest_text = {
        'detail': '在正式评测之前，需要测试您的作答环境是否达到标准。点击下方按钮后您将看到一段文字，请朗读这段文字进行作答。'
                  '<br><br>该题作答完毕后，请按下“提前结束”按钮停止录音。',
        'tip': '为了保证测试准确性，请选择安静环境，并对准麦克风。',
        'content': '床前明月光，疑是地上霜，举头望明月，低头思故乡。'
    }


class ReportConfig(object):
    structure_list = ['sum-aspects', 'aspects', 'example', 'opinion', 'sum']
    logic_list = ['cause-affect', 'transition', 'progressive', 'parallel']

    hit_dict = {
        'sum-aspects': '你在表达时，很好的使用了分层法。分层法是有一种经典的表达方法，也就是我们平时说的总-分结构，它将观点层层剥离，'
                       '是讲述内容更有层次性。自上而下、现总结后具体的表达顺序，能够提前说明你叙述内容之间的逻辑关系，让倾听者对内容做出与你相同的理解。',
        'aspects': '你在交流中，能将内容进行有逻辑的组织。利用分点，将你的观点进行拆分讲解，相信你在平时工作、生活和学习的表达中，也是一名思路清晰，有条理的表达者。',
        'example': '在表达时，合理的使用了举例。例子是表达力必不可少的的元素，它能支撑或强调表达者的观点，增强说服力。',
        'opinion': '在表达时，你能够将自己的观点进行浓缩，用简洁、有力的语言表达自己的观点，让人印象深刻。',
        'sum': '在表达时，你会有意识的在结束进行一个总的回顾，这种前后呼应的表达方式，它能再次强化你的观点，突出内容的重点，加深别人对你的印象。'
               '自下而上的思考，能让你在思考、设计交流内容时，充分完善你的思路，以有效的组织思想的方式，让对方立刻理解你想要表达的信息。'
    }
    not_hit_dict = {
        'sum-aspects': '在表达你的观点，或者进行发言时，你可以适当的使用分层法。分层法是有一种经典的表达方法，'
                       '也就是我们平时说的总-分结构，它将观点层层剥离，是讲述内容更有层次性。',
        'aspects': '在论述复杂话题时，利用分点，将你的观点进行拆分讲解，能让你的表达更清晰。',
        'example': '在表达观点时，你可以适当的使用举例，来证明你的观点。例子是表达力必不可少的的元素，它能支撑或强调表达者的观点，增强说服力。',
        'opinion': '表达中，亮明观点，用简洁、有力的语言表达自己的观点，能够让人印象更深刻。',
        'sum': '当结束活临近话题结尾时，有意识的在结束进行一个总的回顾，这种前后呼应的表达方式，它能再次强化你的观点，突出内容的重点，加深别人对你的印象。'
    }


class DefaultValue(object):
    user_id = 'user_id_placeholder'
    user_name = 'default name'
    question_id = 'question_id_placeholder'
    question_content = 'Default content'
    question_level = 1
    question_type = 1
    used_time = 0
    test_id = "000000000000000000000000"
    session_expire = 3600  # 考试会话默认过期时长
    max_random_try = 20  # 测试初始化随机选题时的最大尝试次数


class Setting(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUTO_REGISTER_IF_USER_NOT_EXISTS = False
    LIMIT_EXAM_TIMES = True
