#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-7


class PathConfig(object):
    parent_abs_path = '/expression'
    audio_save_basedir = 'audio'
    audio_copy_temp_basedir = 'temp_audio'
    audio_extension = '.wav'


class ExamConfig(object):
    answer_time_around = 10
    question_num_each_type = {1: 1, 2: 4, 3: 1}  # q_type:question_numbers
    question_allow_repeat = {1: True, 2: False, 3: True}  # q_type:True/False
    question_limit_time = {1: 60, 2: 30, 3: 120}
    question_prepare_time = {1: 5, 2: 60, 3: 60}
    total_question_num = sum(question_num_each_type.values())
    total_question_type_num = len(question_num_each_type)


class QuestionConfig(object):
    question_type_tip = {
        1: {"detail": "声音质量测试。<br>点击 “显示题目” 按钮后请先熟悉屏幕上的文字，<br>然后按下 “开始回答” 按钮朗读该段文字。", "tip": '为了保证测试准确性，请选择安静环境，并对准麦克风。'},
        2: {"detail": "点击 “显示题目” 后，请先阅读屏幕上的文字。之后，请讲述段落大意及细节信息。", "tip": '约350字，阅读时间一分钟，讲述时间30秒。'},
        3: {"detail": "根据问题发表自己观点。", "tip": "准备1分钟 叙述2分钟"}
    }
