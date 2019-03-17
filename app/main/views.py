#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-22

from . import main
from flask import redirect
from flask import render_template
from flask import session


@main.route('/')
@main.route('/login')
def login():
    session["question_num"] = 0
    session["new_test"] = True
    session["user_name"] = ""
    session["user_id"] = "000000000000000000000000"
    session["test_id"] = "000000000000000000000000"
    return render_template('user/login.html')


@main.route('/welcome')
def welcome():
    session["question_num"] = 0
    session["new_test"] = True
    session["test_id"] = "000000000000000000000000"
    # if session.get("user_name", '') == '':
    #     return redirect("/")
    return render_template('user/welcome.html', user_name=session.get("user_name"), max_question_num=6, answer_time=10)


@main.route('/question', methods=['GET', 'POST'])
def get_question():
    if session.get("user_name", '') == '':
        return redirect("/")
    return render_template('user/question.html', question_num=session.get("question_num", 0))


@main.route('/result')
def get_result():
    session["question_num"] = 0
    if session.get("user_name", '') == '':
        return redirect("/")
    return render_template('user/result.html')
