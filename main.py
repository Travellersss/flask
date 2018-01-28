from flask import Flask
from flask_celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_IMPORT']=('.add_together',)
celery = Celery(app)

@celery.task()
def add_together(a, b):
    return a + b
def hehe():
    s=add_together.delay(23,56)
    print(s.get())
if __name__=='__main__':
    hehe()