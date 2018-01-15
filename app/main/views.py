from flask import render_template,session,url_for,redirect,flash
from ..models import User,Post,Comment,Tag,tags
from . import main
from .. import db
from .forms import UserForm,CommentForm
import datetime
from sqlalchemy import func
from flask import abort
from flask_login import login_required


def siderbar_data():
    recent=Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags=db.session.query(Tag,func.count(tags.c.post_id).label('total')).join(tags).group_by(Tag).order_by('total DESC').limit(5).all()
    return recent , top_tags

# @main.route('/')
# @main.route('/<int:page>')
# def home(page=1):
#     posts=Post.query.order_by(Post.publish_date.desc()).paginate(page,10)
#     recent,top_tags=siderbar_data()
#     return render_template('home.html',posts=posts,recent=recent,top_tags=top_tags)

@main.route('/post/<int:post_id>',methods=['GET','POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name=form.name.data
        new_comment.text=form.text.data
        new_comment.post_id=post_id
        new_comment.date = datetime.datetime.now()
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post',post_id='post_id'))

    post=Post.query.get_or_404(post_id)
    tags=post.tags
    comments=post.comments.order_by(Comment.date.desc()).all()
    recent,top_tags=siderbar_data()

    return render_template('post.html',post=post,tags=tags,comments=comments,form = form ,recent=recent,top_tags=top_tags)

@main.route('/tag/<string:tag_name>')
def tag(tag_name):
    tag=Tag.query.filter_by(title=tag_name).first_or_404()
    posts=tag.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags=siderbar_data()
    return render_template('tag.html', posts=posts, tag=tag,  recent=recent, top_tags=top_tags)



# @main.route('/user/<string:username>')
# def user(username):
#     user=User.query.filter_by(username=username).first_or_404()
#     posts=user.posts.order_by(Post.publish_date.desc()).all()
#     recent,top_tags=siderbar_data()
#     return render_template('user.html',user=user, posts=posts, recent=recent, top_tags=top_tags)

@main.route('/login/',methods =["GET","POST"])
def login():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data)
        if user:
            flash('already login ')
            return redirect(url_for('login'))
        else:
            user = User()
            user.username = form.username.data
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('login.html',form = form )

@main.route('/user/<username>')
@main.route('/user/<username>/<int:page>')
def user(username,page=1):
    user =User.query.filter_by(username =username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.publish_date.desc()).paginate(1,10)
    return render_template('user.html',user = user ,posts=posts)

from .forms import EditProfileForm


@main.route('/edit-profile',methods=["POST","GET"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been update')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)

from ..decorators import admin_required
from .forms import EditProfileAdminForm
from ..models import Role
from flask_login import login_required

@main.route('/edit-profile/<int:id>',methods=["GET","POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email =form.email.data
        user.usernmae=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        db.session.commmit()
        flash('The profile has been updated')
        return redirect(url_for('main.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit_profile.html',form=form,user=user)

from .forms import PostForm
from ..models import Permission
@main.route('/',methods=["POST","GET"])
@main.route('/<int:page>',methods=["POST","GET"])
def index(page=1):
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post =Post(title=form.title.data,content=form.body.data,user = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index',page=1))
    posts=Post.query.order_by(Post.publish_date.desc()).paginate(page,10)
    recent, top_tags = siderbar_data()
    return render_template('home.html',form=form,posts=posts,recent=recent,top_tags=top_tags)

