#coding=utf-8

from flask_wtf import Form
from wtforms import StringField,TextAreaField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,Email
from flask_mail import Mail


class UserForm(Form):
    username = StringField('Please put your email',validators = [DataRequired(),Email()])
    password = PasswordField('Please put your password',validators = [DataRequired(),Length(max=16)])
class CommentForm(Form):

    text=TextAreaField(u'Comment',validators = [DataRequired()])
    submit=SubmitField('提交')

class EditProfileForm(Form):
    name=StringField('Real name',validators =[Length(0,64)])
    location = StringField('Location',validators =[Length(0,64)])
    about_me= TextAreaField('About me')
    submit = SubmitField('Submit')

from wtforms import BooleanField,SelectField
from wtforms.validators import Required,Regexp
from ..models import User,Role
from wtforms import ValidationError

class EditProfileAdminForm(Form):
    #注意在validators中不要少了(),例如Required,会导致报错__init__ takes from 1 to 2 positional arguments but 3 were given
    email = StringField('Email',validators = [Required(),Length(1,64),Email()])
    username =StringField('Username',validators=[Required(),Length(1,64)])
    confirmed = BooleanField('Confirmed')
    role =SelectField('Role',coerce=int)
    name=StringField('Real name',validators =[Length(0,64)])
    location = StringField('Location',validators =[Length(0,64)])
    about_me= TextAreaField('About me')
    submit = SubmitField('Submit')


    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices =[(role.id,role.name)
                            for role in Role.query.order_by(Role.name).all()]
        self.user=user
    def validate_email(self, field):
        if field.data!=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already register')

    def validate_username(self, field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('username already in used')

from flask_pagedown.fields import PageDownField
class PostForm(Form):
    title = StringField('Title',validators = [Required(),Length(1,64)])
    body = PageDownField('请输入你的内容！',validators=[Required()])
    submit= SubmitField('Submit')