#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

from flask import Blueprint

accounts = Blueprint('accounts', __name__)

from .views import *
from .utils import *
