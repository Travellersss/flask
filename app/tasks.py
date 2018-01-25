from flask_mail import Message
from .models import Post

from flask import render_template,current_app
from app import mail,celery
from sqlalchemy import event
@celery.task(bind=True,ignore_result=True,default_retry_delay=300,max_retries=5)
def remind(self,pk):
    post=Post.query.filter_by(id=pk).first()
    users=post.user.followed.all()
    to=[user.email for user in users]
    subject='hello'
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])

    msg.html = render_template('taskpost.html',post=post)
    try:
        mail.send(msg)
    except Exception as e:
        self.retry(exc=e)


@celery.task()
def log(msg):
    return msg
def on_reminder_save(maper,connect,self):
    print('hello')
    remind.delay(self.id)

event.listen(Post,'after_insert',on_reminder_save)