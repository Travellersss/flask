#coding=utf-8
from flask import Flask
from config import DecConfig

app=Flask(__name__)
app.config.from_object(DecConfig)

@app.route('/')
def home():
    return "<html>Hello world !</html>"

if __name__=='__main__':
    app.run()