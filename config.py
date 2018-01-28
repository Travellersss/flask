
#coding=utf-8
import datetime
import os
from celery.schedules import crontab




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
    FLASKY_ADMIN='15182620613@163.com'

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
    CELERY_BROKER_URL='redis://localhost:6379/0'
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['pickle']
    CELERY_IMPORTS = ("app.tasks",)
    #Celery定时执行任务的配置,要使用此方法还需要另开一个窗口运行celery -A manage.celery beat
    CELERYBEAT_SCHEDULE={
        'sendemail-every-week':{
            'task':'app.tasks.sendemail',
            'schedule':crontab(day_of_week=6,hour='10')
        },
    }
