import os
from flask import render_template, redirect, flash, url_for, request, session
from . import auto
from flask_login import login_user,logout_user,login_required
from ..models import User
from .forms import LoginForm,RegisterForm,ResetpwdForm,ResetForm
from .. import db
from ..email import send_email
from flask_login import current_user
from createcode import create_validate_code

@auto.route('/login',methods=["POST","GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        #判断用户存在且密码正确
        if user is not None and user.verify_password(form.password.data):
            #判断验证码（验证码被随机创建后，存储在session['code']中）正确性
            if 'code' in session and \
                session.get('code',None)==form.verification_code.data.upper():
                login_user(user,form.remenber_me.data)
                old_img=session.get('img_url',None)
                if old_img:
                    os.remove('app/static/image/code/'+old_img)
                session.pop('code')
                session.pop('img_url')
                return redirect(request.args.get('next') or url_for('main.index'))
            old_img = session.get('img_url', None)
            if old_img:
                os.remove('app/static/image/code/' + old_img)
            flash(session['code'])
            img_url, strs = create_validate_code()
            session['code'] = strs
            session['img_url'] = img_url
            #输出错误信息
            flash('验证码错误，请重新输入！')
            return render_template('auto/login.html', form=form, img_url=img_url)
        flash('密码或者用户名错误')
    old_img=session.get('img_url',None)
    if old_img:
        os.remove('app/static/image/code/'+old_img)
    img_url,strs=create_validate_code()
    session['code']=strs
    session['img_url']=img_url
    return render_template('auto/login.html',form =form,img_url=img_url)

#验证码获取代码
@auto.route('/createnewcode')
def createnewcode():
    old_img=session.get('img_url',None)
    if old_img:
        os.remove('app/static/image/code/'+old_img)
    img_url,strs=create_validate_code()
    session['code']=strs
    session['img_url']=img_url
    data=img_url
    return data

@auto.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经推出登陆')
    return redirect(url_for('main.index'))


@auto.route('/register',methods=["POST",'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user =User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,'确认你的账户','auto/email/confirm',user=user,token=token)

        flash('邮件确认已发送，请确认')
        return redirect(url_for('main.index'))
    return render_template('auto/register.html',form=form)


@auto.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('你已经确认有的账号了')

    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))

@auto.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.blueprint !='auto':
            print(request.endpoint)
            return redirect(url_for('auto.unconfirmed'))

@auto.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auto/unconfirmed.html')


@auto.route('/confirm')
@login_required
def resendmail():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认你的账户', 'auto/email/confirm', user=current_user, token=token)

    flash('邮件确认已再次发送，请确认')
    return redirect(url_for('main.index'))


@auto.route('/resetpwd',methods=["POST","GET"])
def updatepassword():
    form = ResetpwdForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        login_user(user)
        token=current_user.generate_confirmation_token_password()
        send_email(user.email,'重置密码','auto/email/resetpwd', user=user, token=token)
        flash('请接收你的邮件修改密码！')
        return redirect(url_for('auto.login'))
    return render_template('auto/resetpwd.html',form=form)

@auto.route('resetpwd/<token>',methods=["POST",'GET'])
def comfirmpwd(token):
    form=ResetForm()
    if form.validate_on_submit():
        if current_user.confirmpwd(token):
            current_user.update_password(form.password.data)
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('auto.login'))
    return render_template('auto/resetpwd.html',form=form)



