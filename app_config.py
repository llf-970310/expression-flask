#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-15

from redis import StrictRedis, ConnectionPool

# redis_client = Redis(host='redis-server.expression.hosts', port=6379, db=0, password='ise_expression')
pool = ConnectionPool(host='redis-server.expression.hosts', port=6379, db=0, password='ise_expression')
redis_client = StrictRedis(connection_pool=pool)
# redis_client = Redis(host='127.0.0.1', port=6379, db=0, password=None)


class MongoConfig:
    # for apscheduler client
    # actually these information should be moved to .env file, then loaded here
    host = 'mongo-server.expression.hosts'
    port = 27017
    # {
    # auth = None
    auth = 'SCRAM-SHA-1'  # auth mechanism, set to None if auth is not needed
    user = 'iselab'
    password = 'iselab###nju.cn'
    # }
    db = 'expression'


class BaseConfig(object):
    LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL. 可使用app.logger.exception(msg)，但level没有EXCEPTION
    SECRET_KEY = 'dL28o(19xi54h2?3BX90k92R'
    # SECRET_KEY = os.urandom(24)  # 设为24位的随机字符,重启服务器则上次session清除

    # session
    SESSION_TYPE = 'null'  # null/redis/.., null: use (flask default) cookie
    SESSION_KEY_PREFIX = 'flask-session:'
    SESSION_USE_SIGNER = True  # 是否强制加盐混淆session
    SESSION_PERMANENT = True  # 是否长期有效，false则关闭浏览器失效
    PERMANENT_SESSION_LIFETIME = 7200  # session长期有效则设定session生命周期

    # mongoengine, https://flask-mongoengine.readthedocs.io/en/latest/
    MONGODB_SETTINGS = {
        'db': 'expression_flask',
        'host': '127.0.0.1',
        'port': 27017,
        # if authentication is needed:
        # 'username': 'webapp',
        # 'password': 'pwd123',
        'connect': False  # False: connect when first connect instead of instantiated
    }

    # 自定义
    IGNORE_LOGIN_PASSWORD = False


class DevelopmentConfig(BaseConfig):
    LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL. 可使用app.logger.exception(msg)，但level没有EXCEPTION
    ALLOW_REGISTER = True  # 是否允许自助注册
    WTF_CSRF_ENABLED = False  # 是否开启flask-wtf的csrf保护,默认是True,用postman提交表单测试需要设为False
    SESSION_USE_SIGNER = False
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis_client
    MONGODB_SETTINGS = {
        'db': MongoConfig.db,
        'host': MongoConfig.host,
        'port': MongoConfig.port,
        # if authentication is needed:
        'username': MongoConfig.user,
        'password': MongoConfig.password,
        'connect': False  # False: connect when first connect instead of instantiated
    }
    IGNORE_LOGIN_PASSWORD = False
    NEED_INVITATION = False  # 注册是否需要邀请码
    # 这个好像是微信公众平台的
    WX_APPID = 'wxd7bad9aab33bb581'
    WX_SECRET = 'f45a6fe1aa873577a18098726befd278'
    # 这个是微信小程序的
    WX_APP_APPID = 'wxf44541a8622d9466'
    WX_APP_SECRET = '485afd39d2bc29269030e40c3212855a'
