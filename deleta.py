from main import Tag,Post,db,User


posts=Post.query.filter_by(content=None)
for post in posts:
    print(post.title)
    db.session.delete(post)
db.session.commit()
