import os
from app import create_app
from celery import Celery



def make_celery(app):
    celery=Celery(app.import_name,broker='redis://localhost:6379/0',backend='redis://localhost:6379/0')
    celery.conf.update(app.config)
    TaskBase =celery.Task
    class ContextTask(TaskBase):
        abstract=True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self,*args,**kwargs)

    celery.Task=ContextTask
    return celery


flask_app=create_app()
celery=make_celery(flask_app)


