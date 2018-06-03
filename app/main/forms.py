#coding=utf-8

from flask_wtf import Form
from wtforms import StringField,TextAreaField,PasswordField,SubmitField,SelectField
from wtforms.validators import DataRequired,Length,Email
from flask_mail import Mail
from ..models import Tag
from sqlalchemy.sql.expression import not_

class UserForm(Form):
    username = StringField('请输入邮箱',validators = [DataRequired(),Email()])
    password = PasswordField('请输入密码',validators = [DataRequired(),Length(max=16)])
class CommentForm(Form):

    text=TextAreaField('评论：',validators = [DataRequired()])
    submit=SubmitField('提交')

class EditProfileForm(Form):
    name=StringField('真实姓名',validators =[Length(0,64)])
    location = StringField('所在地',validators =[Length(0,64)])
    about_me= TextAreaField('自我描述')
    submit = SubmitField('提交')

from wtforms import BooleanField,SelectField
from wtforms.validators import Required,Regexp
from ..models import User,Role
from wtforms import ValidationError

class EditProfileAdminForm(Form):
    #注意在validators中不要少了(),例如Required,会导致报错__init__ takes from 1 to 2 positional arguments but 3 were given
    email = StringField('Email',validators = [Required(),Length(1,64),Email()])
    username =StringField('用户名',validators=[Required(),Length(1,64)])
    confirmed = BooleanField('邮件确认')
    role =SelectField('角色',coerce=int)
    name=StringField('真实姓名',validators =[Length(0,64)])
    location = StringField('所在地',validators =[Length(0,64)])
    about_me= TextAreaField('自我描述')
    submit = SubmitField('提交')


    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices =[(role.id,role.name)
                            for role in Role.query.order_by(Role.name).all()]
        self.user=user
    def validate_email(self, field):
        if field.data!=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在')

from flask_pagedown.fields import PageDownField
class PostForm(Form):
    title = StringField('Title',validators = [Required(),Length(1,64)])

    tag=SelectField('请选择一级博文标签！',validators=[Required()],coerce=int)
    lasttag=SelectField('请选择二级博文标签！',validators=[Required()],coerce=int)
    body = PageDownField('请输入你的内容(可拖动输入框右下角改变大小)<a href="'
                         ''
                         ''
                         '" data-toggle="modal" data-target="#imgModal">插入图片</a>', validators=[Required()])
    def __init__(self,*args,**kwargs):
        super(PostForm,self).__init__(*args,**kwargs)
        self.tag.choices=[(tag.id,tag.title) for tag in Tag.query.filter(Tag.parent_id==None).all()]
        self.lasttag.choices=[(tag.id,tag.title) for tag in Tag.query.all()]
    submit= SubmitField('Submit')
