
#coding=utf-8
class Config(object):
    pass
class ProdConfig(Config):
    pass
class DecConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:root@127.0.0.1:3306/flask'
    SQLALCHEMY_ECHO=True

