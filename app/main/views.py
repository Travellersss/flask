import uuid

import os
from flask import render_template, session, url_for, redirect, flash, request, make_response, current_app
from ..models import User,Post,Comment,Tag,tags,Message
from . import main
from ..decorators import permission_required
from .. import db,socketio
from flask_socketio import emit
from .forms import UserForm,CommentForm
import datetime
from sqlalchemy import func
from flask import abort
from flask_login import login_required,current_user
import json
from sqlalchemy.sql.expression import not_,or_
from .forms import PostForm
from app import cache
from flask import jsonify
from ..decorators import admin_required
from .forms import EditProfileAdminForm
from ..models import Role
from flask_login import login_required
from ..models import Permission
from .forms import EditProfileForm
from ..tasks import remind


def siderbar_data():
    recent=Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags=db.session.query(Tag,func.count(tags.c.post_id).label('total')).join(tags).group_by(Tag).order_by('total DESC').limit(5).all()
    return recent , top_tags

@cache.memoize(60)
@main.route('/post/<int:post_id>',methods=['GET','POST'])
def post(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)
    oldclicknum=post.clicknum
    newclicknum=oldclicknum+1
    post.clicknum=newclicknum
    db.session.add(post)
    user=post.user
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.user=current_user

        new_comment.text=form.text.data
        new_comment.post_id=post_id
        new_comment.date = datetime.datetime.now()
        s='{0}对您的文章{1}发表了评论:{2}'.format(current_user.username,post.title,new_comment.text)
        message = Message(user=user, msg=s, comment_username=current_user.username, tag='comment',
                          comment_body=new_comment.text,post_title=post.title,post_id=post.id)
        db.session.add_all([new_comment,message])
        db.session.commit()
        messages=json.loads(str(Message.query.filter_by(status=True,user=user).count()))

        return redirect(url_for('main.post',post_id=post_id))
    tags=post.tags
    comments=post.comments.order_by(Comment.date.desc()).all()
    recent,top_tags=siderbar_data()
    return render_template('post.html',post=post,tags=tags,comments=comments,form = form ,recent=recent,top_tags=top_tags)

@cache.memoize(60)
@main.route('/tags/<tag_title>')
def tag(tag_title):
    if tag_title.isdigit():
        tag=Tag.query.filter_by(id=tag_title).first()
    else:
        tag=Tag.query.filter_by(title=tag_title).first()
    # posts=tag.posts.order_by(Post.publish_date.desc()).all()
    # recent,top_tags=siderbar_data()
    tags=Tag.query.filter_by(parent_id=tag.id).all()
    list=[]
    for t in tags:
        list.append({'id':t.id,'title':t.title})
    return jsonify({'data':list})



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
    return render_template('user.html',user = user,posts=posts)




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

def make_cache_key(*args,**kwargs):
    path=request.path
    args=str(hash(frozenset(request.args.items())))

    cookies=request.cookies.get('show_followed','0')
    return (path+args+cookies).encode('utf-8')


@main.route('/',methods=["POST","GET"])
@main.route('/<int:page>',methods=["POST","GET"])
# @cache.cached(timeout=600,key_prefix=make_cache_key)
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
    tags=Tag.query.filter_by(parent_id=None).all()
    orders=Tag.query.filter(not_(Tag.parent_id==None)).all()
    posts=pagination.items
    recent, top_tags = siderbar_data()
    return render_template('home.html',orders=orders,tags=tags,form=form,posts=posts,recent=recent,top_tags=top_tags,pagination=pagination,show_followed=show_followed)


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
    msg='关注了你'
    message=Message(user=user,msg=msg,comment_username=current_user.username)
    db.session.add_all([current_user,message])
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



@login_required
@main.route('/write_post/',methods=['POST','GET'])
def writePost():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.body.data,user=current_user)
        db.session.add(post)
        db.session.flush()
        db.session.commit()
        post=Post.query.filter_by(title=form.title.data).first()
        post.tags.append(Tag.query.get(form.lasttag.data))
        db.session.add(post)
        db.session.flush()
        db.session.commit()
        # remind(post.id)
        return redirect(url_for('.index'))

    return render_template('writepost.html',form=form)

@main.route('/store/<int:post_id>')
def store(post_id):
    if current_user.is_authenticated:
        post=Post.query.filter_by(id=post_id).first()

        post.storybyuser.append(current_user)
        flash('你已经收藏了此文章，可在我的收藏里面找打它！')
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post',post_id=post_id))
    return redirect(url_for('auto.login'))



@login_required
@main.route('/mystore')
def mystore():
    posts=current_user.storeposts.paginate(1,20)

    return render_template('mystore.html',posts=posts)



@login_required
@main.route('/messages')
def mymessage():
    messages=Message.query.filter_by(user=current_user,status=True).order_by(Message.timestamp).all()
    current_user.messages.update({'status':False})
    db.session.commit()
    return render_template('messages.html',messages=messages)


@login_required
@main.route('/oldmessages')
def show_read_message():
    messages=Message.query.filter_by(user=current_user,status=False).order_by(Message.timestamp).all()
    return render_template('messages.html',messages=messages)

@main.route('/search')
def search():
    keyword=request.args.get('search')


    posts = Post.query.msearch(keyword, fields=['title','content'], limit=20).all()
    if len(posts)==0:
        posts=Post.query.filter(or_(Post.title.contains(keyword),Post.content.contains(keyword))).limit(20).all()
    # posts = search.whoosh_search(Post, query=keyword, fields=['title','content'], limit=20)
    return render_template('searchpost.html',posts=posts)



# @socketio.on('connect', namespace='/test')
# def test_connect():
#     emit('my response', {'data': 'Connected', 'count': 0})
#
#
# @socketio.on('my event', namespace='/test')
# def test_message(message):
#     emit('my response', {'data': message['data'], 'count': 2})


@cache.cached(timeout=60,key_prefix=make_cache_key)
@main.route('/tag/<tag_title>')
@main.route('/tag/<tag_title>/<page>')

def handletag(tag_title,page=1):
    tag=Tag.query.filter_by(title=tag_title).first()
    print(tag.title)
    print('+'*100)
    posts=tag.posts.order_by(Post.publish_date.desc()).paginate(page,20,error_out=False)
    print(posts)
    return render_template('tagposts.html',posts=posts,tag=tag)


@login_required
@main.route('/order',methods=['POST','GET'])
def order():
    tags=request.form.getlist('ordertags[]')
    print('+'*100)
    print(tags)
    user=current_user
    for tag in tags:
        order=Tag.query.filter_by(title=tag).first()
        if user.tags.filter_by(id=order.id).first()==None:
            user.tags.append(order)

            db.session.add(user)
            db.session.flush()
    db.session.commit()
    status='订阅成功'
    return  status


@login_required
@main.route('/removeorder',methods=['POST'])
def removeorder():
    removeorders=request.form.getlist('list[]')
    user = current_user
    print(removeorders)
    for order in removeorders:
        tag=Tag.query.filter_by(title=order).first()
        print(tag.title)
        # user.tags.filter_by(id=tag.id).first()
        user.tags.remove(tag)
        db.session.add(user)
    db.session.commit()
    return '订阅取消成功'

@login_required
@main.route('/getorder')
def getorder():
    user=current_user
    tags=user.tags
    list=[]
    for tag in tags:
        list.append(tag.title)
    data={'alreadyordertags':list}

    return jsonify(data)





@main.route('/userimg/<username>',methods=["POST","GET"])
def handle_userimg(username):

    if request.method=='POST':
        f=request.files['file']
        user = User.query.filter_by(username=username).first()
        if f  and '.' in f.filename and f.filename.rsplit('.',1)[1] in current_app.config['ALLOWED_EXTENSIONS']:
            filename=str(uuid.uuid1())+'.'+f.filename.rsplit('.',1)[1]
            f.save(current_app.config['UPLOAD_FOLDER']+filename)
            old_user_img = user.userimg_url
            if old_user_img:
                os.remove(current_app.config['UPLOAD_FOLDER']+old_user_img)

            user.userimg_url=filename
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.user',username=username))
    return redirect(url_for('main.user',username=username))

@main.route('/insertpostimg',methods=["POST","GET"])
def insertPostimg():
    if request.method=='POST':
        f = request.files['file']

        if f and '.' in f.filename and f.filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']:
            filename = str(uuid.uuid1()) + '.' + f.filename.rsplit('.', 1)[1]
            f.save(current_app.config['UPLOAD_IMG'] + filename)
            return filename
    return redirect(url_for('main.writePost'))