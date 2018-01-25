import os
#coding=utf-8
class Config(object):
    @staticmethod
    def init_app(app):
        pass
class ProdConfig(Config):
    pass
class DecConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:root@127.0.0.1:3306/flask'
    SQLALCHEMY_ECHO=True
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    SECRET_KEY='python'
    MAIL_USERNAME='15182620613@163.com'
    MAIL_PASSWORD='huimie123'
    MAIL_SERVER='smtp.163.com'
    MAIL_PORT='465'
    MAIL_USE_SSL=True
    MAIL_USE_TLS = False
    FLASKY_MAIL_SUBJECT_PREFIX='Flasky'
    FLASKY_MAIL_SENDER='15182620613@163.com'
    FLASKY_ADMIN='15182620613@163.com '

    MSEARCH_INDEX_NAME = 'whoosh_index'

    # simple,whoosh

    MSEARCH_BACKEND = 'whoosh'

    # 自动生成或更新索引

    MSEARCH_ENABLE = True
    # WHOOSH_BASE = 'mysql+pymysql://root:root@127.0.0.1:3306/flask'
    # MAX_SEARCH_RESULTS = 50
    WHOOSH_BASE = 'whoosh_index'
    WHOOSH_ENABLE = True

    # 缓存设置
    CACHE_TYPE='simple'

    #Celery配置
    CELERY_BROKER_URL='amqp://guest:guest@localhost:5672//'
    CELERY_BACKEND='amqp://guest:guest@localhost:5672//'
