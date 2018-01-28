import datetime
from sqlalchemy.sql.expression import not_
from flask_mail import Message
from .models import Post, User, orders

from flask import render_template,current_app
from app import mail,celery,db

# from sqlalchemy import event
@celery.task(bind=True,ignore_result=True,default_retry_delay=300,max_retries=5)
def remind(self,pk):
    #发送邮件给文章主人的关注者们
    post=Post.query.filter_by(id=pk).first()
    users=post.user.followers.all()
    to=[User.query.filter_by(id=user.follower_id).first().email for user in users]
    subject='hello,flask'
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=to)

    msg.html = render_template('taskpost.html',post=post)
    try:
        mail.send(msg)
    except Exception as e:
        self.retry(exc=e)



@celery.task(bind=True,ignore_result=True,default_retry_delay=300,max_retries=5)
def sendemail():
    year, week = datetime.datetime.now().isocalendar()[0:2]
    date = datetime.date(year, 1, 1)
    if (date.weekday() > 3):
        date = date + datetime.timedelta(7 - date.weekday())
    else:
        date = date - datetime.timedelta(date.weekday())
    delta = datetime.timedelta(days=(week - 1) * 7)
    start, end = date + delta, date + delta + datetime.timedelta(days=6)

    users=User.query.filter(not_(User.tags!=None)).all()

    for user in users:
        tags=user.tags
        email=user.email
        posts = Post.query.filter(Post.publish_date >= start, Post.publish_date <= end,Post.tags.in_(tags)).limit(50).all()
        app=current_app._get_current_object()
        subject='每周精选'
        msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                      recipients=[email])
        msg.html=render_template('weekpost.html',posts=posts)

        mail.send(msg)




@celery.task()
def multiply(a,b):
    return a+b


@celery.task()
def log(msg):
    return msg

def on_reminder_save(maper,connect,self):

    remind.delay(self.id)

db.event.listen(Post,'after_insert',on_reminder_save)