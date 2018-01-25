from flask import Flask,render_template
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from  config import DecConfig
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_msearch import Search
from jieba.analyse import ChineseAnalyzer
from flask_socketio import SocketIO,emit
from flask_cache import Cache
from flask_celery import Celery

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auto.login'

cache=Cache()
celery=Celery()
mail=Mail()
moment = Moment()
bootsrap = Bootstrap()
db = SQLAlchemy()
socketio=SocketIO()
search = Search(db=db,analyzer=ChineseAnalyzer())


pagedown = PageDown()

def create_app():
    app = Flask(__name__)
    app.config.from_object(DecConfig)
    bootsrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    search.init_app(app)
    pagedown.init_app(app)
    socketio.init_app(app)
    cache.init_app(app)
    celery.init_app(app)
    db.init_app(app)



    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    from .auto import auto as auto_blueprint
    app.register_blueprint(auto_blueprint ,url_prefix='/auto')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api')
    return app
