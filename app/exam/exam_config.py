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
        'content': '表达力测试将用15分钟的时间，数据化您的表达能力。'
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
