from . import admin
from app.exam.util import *
from app.models.user import UserModel
from app import errors
from app.models.exam import *
from flask import request, current_app, jsonify, session
from . import mock_data
import datetime


@admin.route('/questions', methods=['GET'])
def get_all_questions():
    return jsonify(errors.success(mock_data.questions))
