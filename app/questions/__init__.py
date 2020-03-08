#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-03-08

from flask import Blueprint

questions = Blueprint('questions', __name__)

from . import feedback_views
