from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,EqualTo,Regexp
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])

    password = PasswordField('密码',validators =[Required()])
    verification_code=StringField('验证码',validators=[Required()])
    remenber_me = BooleanField('keep me logged in')
    submit = SubmitField('登陆')


class  RegisterForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(6,64)])

    password = PasswordField('密码', validators=[Required(),EqualTo('password2',message='password must match.')])
    password2 =PasswordField('确认密码',validators = [Required()])
    submit = SubmitField('注册')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already register')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('username already in used')

class  ResetpwdForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])

    submit = SubmitField('发送邮件')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() == None:
            raise ValidationError('用户不存在')


class  ResetForm(Form):

    password = PasswordField('请输入新密码', validators=[Required(),EqualTo('password2',message='password must match.')])
    password2 =PasswordField('确认密码',validators = [Required()])
    submit = SubmitField('提交')
