from . import login_manager
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW =0x01
    COMMENT =0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80


class Role(db.Model):

    id = db.Column(db.Integer,primary_key =True)
    name = db.Column(db.String(64),unique = True)
    default = db.Column(db.Boolean,default =False,index=True)
    permissions = db.Column(db.Integer)
    users= db.relationship('User',backref ='role',lazy= 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW |Permission.COMMENT |Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW |Permission.COMMENT | Permission.WRITE_ARTICLES |Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role == None:
                role = Role()
                role.name = r
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
    def __repr__(self):
        return self.name


import hashlib
from flask import request
class User(UserMixin,db.Model):

    id=db.Column(db.Integer(),primary_key=True)
    email = db.Column(db.String(64),unique=True,index =True)
    username=db.Column(db.String(255))
    password_hash=db.Column(db.String(255))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    merber_since = db.Column(db.DateTime(),default =datetime.utcnow())
    last_seen =db.Column(db.DateTime(),default = datetime.utcnow())
    avatar_hash=db.Column(db.String(32))
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))
    posts=db.relationship('Post',backref='user',lazy='dynamic')


    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()


        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url='http://secure.gravatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'
        hash=self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)

    def ping(self):
        self.last_seen =datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def can(self,permissions):
        return self.role is not None and (self.role.permissions& permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


    @property
    def password(self):
        raise AttributeError('password not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def update_password(self,password):
        self.password_hash =generate_password_hash(password)

    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id:
            return False

        self.confirmed=True
        db.session.add(self)

        return True

    def generate_confirmation_token_password(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'password':self.id})
    def confirmpwd(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('password') != self.id:
            return False
        return True


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u =User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),

                    name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence(),
                    merber_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser
tags=db.Table('post_tags',
              db.Column('post_id',db.Integer(),db.ForeignKey('post.id')),
              db.Column('tag_id',db.Integer(),db.ForeignKey('tag.id'))
              )

class Post(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title = db.Column(db.String(255))
    content=db.Column(db.Text())

    publish_date=db.Column(db.DateTime(),index=True,default =datetime.utcnow)
    comments=db.relationship('Comment',backref='post',lazy='dynamic')
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))
    tags=db.relationship('Tag',secondary=tags,backref=db.backref('posts',lazy='dynamic'))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed,randint
        import forgery_py
        seed()
        user_count=User.query.count()

        for i in range(count):
            u=User.query.offset(randint(0,user_count-1)).first()
            p=Post(title=forgery_py.lorem_ipsum.sentence(),
                   content=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                   publish_date=forgery_py.date.date(True),
                   user=u)
            db.session.add(p)
            db.session.commit()

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

