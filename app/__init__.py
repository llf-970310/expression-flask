#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-15

from app import errors
from app_config import DevelopmentConfig
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_mongoengine import MongoEngine

import os
import sys
prj_folder = os.path.abspath(__file__).split('/app/__init__.py')[0]
analysis_docker_folder = (os.path.join(prj_folder, 'analysis-docker'))
sys.path.append(analysis_docker_folder)
sys.path.append(os.path.join(analysis_docker_folder, 'expression'))


db = MongoEngine()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.unauthorized = lambda: jsonify(errors.Login_required)


def create_app():
    app = Flask(__name__, static_url_path='/static')  # 要映射静态文件到根目录下用static_url_path=''

    app.config.from_object(DevelopmentConfig)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    if app.config['SESSION_TYPE'] != 'null':
        from flask_session import Session
        Session(app)
    db.init_app(app)
    login_manager.init_app(app)

    # -------------------------------------------apscheduler init
    from app.async_tasks import APScheduler, SchedulerConfig
    scheduler = APScheduler()
    app.config.from_object(SchedulerConfig)
    from app.async_tasks import AvailableJobs
    from app.models.apscheduler import ApJob

    stored_jobs = ApJob.objects()
    stored_job_ids = [j.get_id() for j in stored_jobs]
    app.config['JOBS'] = AvailableJobs.get_new_available_jobs(stored_job_ids)
    print('--------- new apscheduler available jobs ---------')
    print(app.config['JOBS'])
    print('--------------------------------------------------')
    scheduler.init_app(app)
    scheduler.start()
    scheduler._logger = app.logger
    # ---------------------------------------apscheduler init end

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    from .exam import exam as exam_blueprint
    app.register_blueprint(exam_blueprint, url_prefix='/api/exam')
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    from .account import account as accounts_blueprint
    app.register_blueprint(accounts_blueprint, url_prefix='/api/account')
    from .questions import questions as questions_blueprint
    app.register_blueprint(questions_blueprint, url_prefix='/api/questions')
    from .async_tasks import ap_view as ap_view_blueprint
    app.register_blueprint(ap_view_blueprint, url_prefix='/api/apscheduler')

    return app
