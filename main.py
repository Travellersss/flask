#coding=utf-8
from flask import Flask
from config import DecConfig
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config.from_object(DecConfig)
db=SQLAlchemy(app)

@app.route('/')
def home():
    return "<html>Hello world !</html>"

class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(255))
    password=db.Column(db.String(255))
    posts=db.relationship('Post',backref='user',lazy='dynamic')
    def __init__(self, username):
        self.username= username
    def __repr__(self):
        return self.username

tags=db.Table('post_tags',db.Column('post_id',db.Integer(),db.ForeignKey('post.id')),
              db.Column('tag_id',db.Integer(),db.ForeignKey('tag.id')))

class Post(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    content=db.Column(db.Text())
    title=db.Column(db.String(255))
    publish_date=db.Column(db.DateTime())
    comments=db.relationship('Comment',backref='post',lazy='dylamic')
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))
    tags=db.relationship('Tag',secondary=tags,backref=db.backref('posts',lazy='dylamic'))
    def __init__(self,title):
        self.title=title
    def __repr__(self):
        return self.title
class Comment(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(255))
    text=db.Column(db.Text())
    date=db.Column(db.DateTime())
    post_id=db.Column(db.Integer(),db.ForeignKey('post.id'))

    def __repr__(self):
        return self.text[:15]



class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    def __init__(self,title):
        self.title=title
    def __repr__(self):
        return self.title

if __name__=='__main__':
    app.run()