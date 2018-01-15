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
    FLASKY_ADMIN='15182620613@163.com'