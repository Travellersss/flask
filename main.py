#coding=utf-8
from flask import Flask
from config import DecConfig
from flask.ext.sqlalchemy import SQLAlchemy

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
    def __init__(self,username):
        self.username=username


    def __repr__(self):
        return self.username
if __name__=='__main__':
    app.run()