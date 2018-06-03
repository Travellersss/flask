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


@main.route('/liketoggle/<status>/<post_id>')
def liketoggle(status,post_id):
    post=Post.query.filter_by(id=post_id).first()
    if current_user.is_authenticated:

        if status == 'like':
            post.liked.append(current_user)
            post.weight_value = 0.1 * post.clicknum + 0.3 * len(post.liked) + 0.5 * post.comments.count()
            msg=Message(post_id=post_id,comment_username = current_user.username,tag='like',user_id=post.user.id)
            db.session.add(msg)


        else:
            post.liked.remove(current_user)

            post.weight_value = 0.1 * post.clicknum + 0.3 * len(post.liked) + 0.5 * post.comments.count()

        db.session.add(post)
        db.session.commit()
        data =[{'likenum':len(post.liked)}]
        return jsonify(data)
    return redirect(url_for('auto.login'))

@cache.memoize(60)
@main.route('/post/<int:post_id>')
@main.route('/post/<int:post_id>/<page>')
def post(post_id,page=1):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        if not current_user in post.records:
            post.records.append(current_user)
    post.clicknum=post.clicknum+1
    post.weight_value=0.1*post.clicknum + 0.3*len(post.liked)+0.5*post.comments.count()
    db.session.add(post)
    db.session.commit()
    user=post.user
    tags=post.tags
    pagination = post.comments.order_by(Comment.date.desc()).filter_by(parent_id=None).paginate(1,10)
    comments=pagination.items
    if tags[0]:
        s = str(tags[0])
        tag = Tag.query.filter_by(title=s).first()
        posts=tag.posts.order_by(Post.weight_value.desc(),Post.publish_date.desc()).limit(5).all()
    else:
        posts = Post.query.order_by(Post.weight_value.desc(),Post.publish_date.desc()).limit(5).all()
    recent,top_tags=siderbar_data()
    orders = Tag.query.filter(not_(Tag.parent_id == None)).all()
    storypostnum= len(post.storybyuser)
    likenum=len(post.liked)
    readnum=len(post.records)
    return render_template('post.html',likenum=likenum,readnum=readnum,post=post,tags=tags,comments=comments,recent=recent,top_tags=top_tags,orders=orders,storypostnum=storypostnum,pagination=pagination,posts=posts)



@cache.memoize(60)
@main.route('/tags/<tag_title>')
def tag(tag_title):

    if tag_title.isdigit():
        tag=Tag.query.filter_by(id=tag_title).first()
    else:
        tag=Tag.query.filter_by(title=tag_title).first()
    # posts=tag.posts.order_by(Post.publish_date.desc()).all()
    # recent,top_tags=siderbar_data()
    tags=tag.childrens
    print('+'*120)
    print(tags)
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
            flash('已经登录')
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
    posts = user.posts.order_by(Post.publish_date.desc()).paginate(page,10)

    return render_template('user.html',user = user,posts=posts)



#用户修改个人信息
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
        flash('你的个人信息已经更新')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)


#管理员修改用户信息
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
        flash('个人信息已更新')
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
    #判断用户是否登录，只有登录后，才可查看他所关注作者的博文
    if current_user.is_authenticated:
        show_followed =bool(request.cookies.get('show_followed',''))
    if show_followed:
        query=current_user.followed_posts
    else:
        query=Post.query
    pagination=query.order_by(Post.publish_date.desc())\
    .paginate(page,20,error_out=False)
    tags=Tag.query.filter_by(parent_id=None).all()
    orders=Tag.query.filter(not_(Tag.parent_id==None)).all()
    posts=pagination.items
    #推荐文章
    recent=Post.query.order_by(Post.weight_value.desc(),\
        Post.publish_date.desc()).limit(8).all()

    return render_template('home.html',orders=orders,tags=tags,form=form,\
    posts=posts,recent=recent,pagination=pagination,show_followed=show_followed)



@main.route('/commentpage/<page>')
def commentpage(page=1):
    pass

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
        flash('博文已经更改完成')
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
        flash('用户不存在')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已经关注过他了')
        return redirect(url_for('main.user',username=username))
    current_user.follow(user)

    message=Message(user=user,comment_username=current_user.username,tag='follow')
    db.session.add_all([current_user,message])
    db.session.commit()
    flash('你已经关注他了')
    return redirect(url_for('main.user',username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username).first()

    if  not current_user.is_following(user):
        flash('你并没有关注此用户')
        return redirect(url_for('main.user',username=username))
    current_user.unfollow(user)
    flash('你已经取消对此用户的关注')
    return redirect(url_for('.user',username=username))

@main.route('/followtoggle/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def followtoggle(username):
    user = User.query.filter_by(username=username).first()
    if current_user.is_following(user):
        current_user.unfollow(user)

        return 'unfollow'
    else:
        current_user.follow(user)
        message = Message(user=user,comment_username=current_user.username, tag='follow')
        db.session.add_all([current_user, message])
        db.session.commit()
        return 'follow'

from flask import request
@main.route('/followers/<username>')
def followers(username):
    user =User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('main.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.paginate(page,20)
    follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title='Followers of ',endpoint='.followers',pagination=pagination,follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user =User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在此用户')
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

    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.post',post_id=post_id))




@login_required
@main.route('/store/<int:post_id>')
def store(post_id):
    if current_user.is_authenticated:
        post=Post.query.filter_by(id=post_id).first()

        post.storybyuser.append(current_user)
        flash('你已经收藏了此文章，可在我的收藏里面找打它！')
        msg=Message()
        msg.tag='store'
        msg.comment_username=current_user.username
        msg.post_title=post.title
        msg.post_id=post.id
        db.session.add(msg)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post',post_id=post_id))
    return redirect(url_for('auto.login'))



@login_required
@main.route('/mystore')
@main.route('/mystore/<page>')
def mystore(page=1):
    posts=current_user.user.paginate(page,20)

    return render_template('mystore.html',posts=posts)


@main.route('/remstore/<post_id>')
def removestore(post_id):
    post = Post.query.filter_by(id=post_id).first()

    post.storybyuser.remove(current_user)

    flash('你已经移除了此文章！')
    db.session.add(post)
    db.session.flush()
    db.session.commit()
    return redirect(url_for('.mystore'))



@login_required
@main.route('/messages/<tag>')
def mymessage(tag):
    messages=Message.query.filter_by(user=current_user,status=True,tag=tag).order_by(Message.timestamp).all()
    current_user.messages.filter_by(tag=tag).update({'status':False})
    db.session.commit()
    orders = Tag.query.filter(not_(Tag.parent_id == None)).all()
    return render_template('messages.html',messages=messages,tag=tag,orders=orders)


@login_required
@main.route('/oldmessages/<tag>')
def show_read_message(tag):
    orders = Tag.query.filter(not_(Tag.parent_id == None)).all()
    messages=Message.query.filter_by(user=current_user,status=False,tag=tag).order_by(Message.timestamp).all()
    return render_template('messages.html',messages=messages,tag=tag,orders=orders)

@login_required
@main.route('/removemsg/<msg_id>')
def removemessage(msg_id):
    msg=Message.query.filter_by(id=msg_id).first()
    if msg:
        db.session.delete(msg)
        db.session.commit()
    return redirect(request.args.get('next') or url_for('main.show_read_message',tag='comment'))

@main.route('/search')
def search():
    keyword=request.args.get('search')
    posts = Post.query.whoosh_search(keyword).\
        order_by(Post.weight_value.desc(),Post.publish_date.desc()).all()
    if len(posts)==0:
        posts=Post.query.filter(or_(Post.title.contains(keyword),\
        Post.content.contains(keyword))).order_by(Post.weight_value.desc(),\
        Post.publish_date.desc()).limit(20).all()
    orders = Tag.query.filter(not_(Tag.parent_id == None)).all()
    return render_template('searchpost.html',posts=posts,orders=orders)



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

    posts=tag.posts.order_by(Post.publish_date.desc()).paginate(page,20,error_out=False)
    print(posts)
    orders = Tag.query.filter(not_(Tag.parent_id == None)).all()
    return render_template('tagposts.html',posts=posts,tag=tag,orders=orders)


@login_required
@main.route('/order',methods=['POST','GET'])
def order():
    tags=request.form.getlist('ordertags[]')
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


import flask_whooshalchemyplus
@login_required
@main.route('/write_post/',methods=['POST','GET'])
def writePost():
    form=PostForm()
    if form.validate_on_submit():
        if 'post_img' in session and session.get('post_img',None):
            post_img=session.get('post_img',None)
            session.pop('post_img')
            post=Post(title=form.title.data,content=form.body.data,user=current_user,post_img=post_img)

        else:
            post=Post(title=form.title.data,content=form.body.data,user=current_user)
        db.session.add(post)
        db.session.flush()
        db.session.commit()

        post.tags.append(Tag.query.get(form.lasttag.data))
        db.session.add(post)
        db.session.flush()
        db.session.commit()
        # remind(post.id)
        # flask_whooshalchemyplus.index_one_model(post)
        return redirect(url_for('.index'))

    return render_template('writepost.html',form=form)


@main.route('/insertpostimg',methods=["POST","GET"])
def insertPostimg():
    if request.method=='POST':
        f = request.files['file']

        if f and '.' in f.filename and f.filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']:
            filename = str(uuid.uuid1()) + '.' + f.filename.rsplit('.', 1)[1]
            f.save(current_app.config['UPLOAD_IMG'] + filename)
            if 'post_img' not in session :
                session['post_img']='image/postimg/' + filename
            return filename
    return redirect(url_for('main.writePost'))

# @login_required
# @main.route('/comment/<post_id>',methods=["GET","POST"])
# def comment(post_id):
#     comment = Comment()
#     comment.text = request.form.get('text')
#
#     comment.post_id = post_id
#     comment.user_id = current_user.id
#     db.session.add(comment)
#     db.session.commit()
#     post = Post.query.get_or_404(post_id)
#     post.weight_value = 0.1 * post.clicknum + 0.3 * len(post.liked) + 0.5 * post.comments.count()
#
#     message = Message(tag='comment', post_id=post_id, comment_username=current_user.username, comment_body=comment.text,
#                       post_title=post.title, comment_id=comment.id, user_id=post.user.id)
#     db.session.add_all([message, post])
#     db.session.commit()
#     return redirect(request.args.get('next') or url_for('main.post',post_id=post_id))
#

@login_required
@main.route('/commentreply/<postid>',methods=["POST","GET"])
def replycomment(postid):
    if current_user.is_authenticated:

        comment=Comment()
        comment.text =request.form.get('input')
        if not comment.text:
            comment.text=request.form.get('text')
        comment.post_id=postid
        comment.user_id=current_user.id
        db.session.add(comment)
        db.session.commit()
        post=Post.query.get_or_404(postid)
        post.weight_value = 0.1 * post.clicknum + 0.3 * len(post.liked) + 0.5 * post.comments.count()

        message = Message(tag='comment',post_id=postid,comment_username=current_user.username,comment_body=comment.text,post_title=post.title,comment_id=comment.id,user_id=post.user.id)
        db.session.add_all([message,post])
        db.session.commit()

        username = comment.user.username
        comment_text = comment.text
        comment_time = comment.date

        if current_user.userimg_url:
            comment_user_img = current_user.userimg_url
        else:
            comment_user_img = '010a1b554c01d1000001bf72a68b37.jpg@1280w_1l_2o_100sh.png'
        data={'username':username,'comment_text':comment_text,'comment_time':comment_time,'comment_user_img':comment_user_img}
        return jsonify(data)
    return redirect(url_for('auto.login'))


@login_required
@main.route('/commentchildren/<postid>/<commentid>',methods=["POST","GET"])
def comment(postid,commentid):
    if current_user.is_authenticated:
        comment = Comment()
        comment.post_id = postid
        comment.user_id = current_user.id
        comment.parent_id = commentid
        comment.text = request.form.get('input')
        db.session.add(comment)
        db.session.commit()
        post = Post.query.get_or_404(postid)
        post.weight_value = 0.1 * post.clicknum + 0.3 * len(post.liked) + 0.5 * post.comments.count()

        message = Message(tag='comment', post_id=postid, comment_username=current_user.username, comment_body=comment.text,
                          post_title=post.title, comment_id=comment.id,user_id=post.user.id)

        db.session.add_all([message,post])
        db.session.commit()

        username = current_user.username
        u = comment.text.split(' ')[0]
        comment_text = comment.text
        comment_time = comment.date
        comment_id=comment.id
        pcomment_id=commentid
        data={'username':username,'u':u,'comment_text':comment_text,'comment_time':comment_time,'comment_id':comment_id,'pcomment_id':pcomment_id}
        return jsonify(data)


    return redirect(url_for('auto.login'))


#用户喜欢
@login_required
@main.route('/likes/<post_id>')
def like(post_id):
    post=Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        if current_user not in post.liked:
            post.liked.append(current_user)
            post.likenum=post.likenum+1
            db.session.add(post)
            db.session.commit()
            msg=Message()
            msg.msg='表示喜欢'
            msg.tag='like'
            msg.post_title=post.title
            msg.post_id=post_id
            msg.user_id=current_user.id
            msg.comment_username=current_user.username
            db.session.add(msg)
            db.session.commit()
        return redirect(request.args.get('next') or url_for('.post',post_id=post_id))
    return redirect(url_for('auto.login'))

@permission_required(Permission.MODERATE_COMMENTS or Permission.ADMINISTER)

@main.route('/removepost/<post_id>')
def removepost(post_id):
    post = Post.query.filter_by(id=post_id).first()

    db.session.delete(post)
    db.session.commit()
    return redirect(request.args.get('next') or url_for('.user',username=current_user.username))

from datetime import datetime,timedelta
@main.route('/hotposts/<int:status>')
def hotposts(status):
    start=datetime.now()-timedelta(days=status)
    if status==7:
        img='/static/7.png'
    else:
        img='/static/30.png'
    posts=Post.query.filter(Post.publish_date >=start).order_by(Post.weight_value.desc(),Post.publish_date.desc()).all()
    return render_template('hotpost.html',posts=posts,img=img)