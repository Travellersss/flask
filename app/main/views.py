from flask import render_template,session,url_for,redirect,flash
from ..models import User,Post,Comment,Tag,tags
from . import main
from .. import db
from .forms import UserForm,CommentForm
import datetime
from sqlalchemy import func
from flask import abort
from flask_login import login_required,current_user


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
        new_comment.user=current_user

        new_comment.text=form.text.data
        new_comment.post_id=post_id
        new_comment.date = datetime.datetime.now()
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('main.post',post_id=post_id))

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
    posts=posts
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
from ..models import Permission

@main.route('/edit-profile/<int:id>',methods=["GET","POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
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
    show_followed=False
    if current_user.is_authenticated:
        show_followed =bool(request.cookies.get('show_followed',''))
    if show_followed:
        query=current_user.followed_posts
    else:
        query=Post.query
    pagination=query.order_by(Post.publish_date.desc()).paginate(page,20,error_out=False)

    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post =Post(title=form.title.data,content=form.body.data,user = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index',page=1))
    posts=pagination
    recent, top_tags = siderbar_data()
    return render_template('home.html',form=form,posts=posts,recent=recent,top_tags=top_tags,pagination=pagination,show_followed=show_followed)


@main.route('/edit/<int:id>',methods=["POST",'GET'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user != post.user and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form =PostForm()
    if form.validate_on_submit():
        post.titlt=form.title.data
        post.content =form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated')
        return redirect(url_for('main.post',post_id=post.id))
    form.title.data=post.title
    form.body.data=post.content
    return render_template('edit_post.html',form=form)

from ..decorators import permission_required
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid User')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注过他了')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)
    db.session.add(current_user)
    db.session.commit()
    flash('你已经关注他了')
    return redirect(url_for('main.user',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username)
    if user is not None:
        flash('Invalid User' )
        return redirect('main.user',username=username)
    if  not current_user.is_following:
        flash('你并没有关注此用户')
        return redirect('main.user',username=username)
    current_user.unfollow()
    flash('你已经取消对此用户的关注')
    return redirect(url_for('mian.index'))


from flask import request
@main.route('/followers/<username>')
def followers(username):
    user =User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.paginate(page,20)
    follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followers of ',endpoint='.followers',pagination=pagination,follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user =User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed.paginate(page,20)
    follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followed of ', endpoint='.followed_by',pagination=pagination, follows=follows)

from flask import make_response
@main.route('/all')
@login_required
def show_all():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp

@login_required
@permission_required(Permission.MODERATE_COMMENTS or Permission.ADMINISTER)
@main.route('/delete_comment/<int:post_id>/<int:id>')
def delete_comment(post_id,id):
    comment=Comment.query.get_or_404(id)
    comment.disable=True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.post',post_id=post_id))


@login_required
@permission_required(Permission.MODERATE_COMMENTS or Permission.ADMINISTER)
@main.route('/recover_comment/<int:post_id>/<int:id>')
def recover_comment(post_id,id):
    comment=Comment.query.get_or_404(id)
    comment.disable=False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.post',post_id=post_id))