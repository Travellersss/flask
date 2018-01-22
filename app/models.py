from . import login_manager
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,url_for
from datetime import datetime
from markdown import markdown
import bleach
from app.exceptions import ValidationError


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


class Follow(db.Model):
    __tablename__='follows'
    follower_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    followed_id =db.Column(db.Integer,db.ForeignKey('user.id'),primary_key =True)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow())

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
    comments=db.relationship('Comment',backref='user',lazy='dynamic')
    messages=db.relationship('Message',backref='user',lazy='dynamic')
    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],
                             backref=db.backref('follower',lazy='joined'),
                             lazy='dynamic',
                             cascade='all,delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')


    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()


        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)
    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self,user):
        return self.followers.filter_by(
            follower_id=user.id
        ).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.user_id).filter(Follow.follower_id==self.id)


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


    def generate_auth_token(self,expiration):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id':self.id}).decode('utf-8')


    @staticmethod
    def verify_auth_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return None
        return User.query.get(data['id'])



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

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'merber_since': self.merber_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user

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
store=db.Table('user_posts',
               db.Column('user_id',db.Integer(),db.ForeignKey('user.id')),
               db.Column('post_id',db.Integer(),db.ForeignKey('post.id')))



class Post(db.Model):
    __searchable__ = ['title', 'content']
    id=db.Column(db.Integer(),primary_key=True)
    title = db.Column(db.String(255))
    content=db.Column(db.Text())

    publish_date=db.Column(db.DateTime(),index=True,default =datetime.utcnow)
    body_html=db.Column(db.Text)
    comments=db.relationship('Comment',backref='post',lazy='dynamic')
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))
    storybyuser=db.relationship('User',secondary=store,backref=db.backref('storeposts',lazy='dynamic'))
    tags=db.relationship('Tag',secondary=tags,backref=db.backref('posts',lazy='dynamic'))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.content,
            'body_html': self.body_html,
            'timestamp': self.publish_date,
            'author_url': url_for('api.get_user', id=self.user_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }

        return json_post

    @staticmethod
    def from_json(json_post):
        body=json_post.get('body')
        if body is None or body=='':
            raise ValidationError('post does not have a body')
        return Post(body=body)
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

    @staticmethod
    def on_changed_body(target,value,oldvalue,initator):
        allowed_tags =['a','abbr','acronym','b','blockquote','code','em','li','i','ol','pre','strong','ul','h1',
                       'h2','h3','h4','p']
        target.body_html =bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))

    def __repr__(self):

        return self.title

class Comment(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    body_html=db.Column(db.Text)
    text=db.Column(db.Text())
    date=db.Column(db.DateTime(),index=True,default=datetime.utcnow())
    disable=db.Column(db.Boolean)
    post_id=db.Column(db.Integer(),db.ForeignKey('post.id'))
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))
    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.user_id),
        }
        return json_comment

    @staticmethod
    def on_changed_body(target, value, oldvalue, initator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'li', 'i', 'ol', 'pre', 'strong', 'ul',
                        'h1',
                        'h2', 'h3', 'h4', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    def __repr__(self):
        return self.text[:15]


db.event.listen(Comment.text,'set',Comment.on_changed_body)
class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    def __init__(self,title):
        self.title=title
    def __repr__(self):
        return self.title


class Message(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    status=db.Column(db.Integer(),default=True)
    timestamp=db.Column(db.DateTime(),default=datetime.utcnow())
    msg=db.Column(db.String(255))
    tag=db.Column(db.String(255))
    comment_username=db.Column(db.String(255))
    comment_body=db.Column(db.String(255))
    post_title=db.Column(db.String(255))
    post_id=db.Column(db.String(255))
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'))
    def __repr__(self):
        return self.msg






