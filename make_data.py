import random
import datetime
from main import Tag,Post,db,User


user=User.query.get(1)
tag_one=Tag('Python')
tag_two=Tag('Flask')
tag_three=Tag('SQLAlchemy')
tag_four=Tag('Jinja2')
tag_list=[tag_one,tag_two,tag_three,tag_four]

s='Example Text'
post=Post.query.all()
db.session.delete(post)
db.session.commit()
for i in range(100):
    new_post=Post('Post'+str(i))
    new_post.user=user
    new_post.publish_date=datetime.datetime.now()
    new_post.content=s+str(i)
    new_post.tags=random.sample(tag_list,random.randint(1,3))
    db.session.add(new_post)
db.session.commit()