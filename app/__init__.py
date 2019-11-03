#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-15

from app_config import DevelopmentConfig
from flask import Flask
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_apscheduler import APScheduler as _BaseAPScheduler

import os
import sys
prj_folder = os.path.abspath(__file__).split('/app/__init__.py')[0]
analysis_docker_folder = (os.path.join(prj_folder, 'analysis-docker'))
sys.path.append(analysis_docker_folder)
sys.path.append(os.path.join(analysis_docker_folder, 'expression'))


class APScheduler(_BaseAPScheduler):
    def run_job(self, id, jobstore=None):
        with self.app.app_context():
            super().run_job(id=id, jobstore=jobstore)


db = MongoEngine()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__, static_url_path='/static')  # 要映射静态文件到根目录下用static_url_path=''

    app.config.from_object(DevelopmentConfig)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    if app.config['SESSION_TYPE'] != 'null':
        from flask_session import Session
        Session(app)
    db.init_app(app)

    from celery_config import CeleryConfig
    app.config.from_object(CeleryConfig)
    scheduler.init_app(app)  # 把任务列表放进flask
    scheduler.start()  # 启动任务列表

    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, static_folder='static')
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    from .exam import exam as exam_blueprint
    app.register_blueprint(exam_blueprint, url_prefix='/api/exam')
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    from .accounts import accounts as accounts_blueprint
    app.register_blueprint(accounts_blueprint, url_prefix='/api/accounts')

    app.md5_hash = app.config['MD5_HASH']

    return app
