from flask.ext.script import Manager,Server
from main import app,User,db,Post
manager=Manager(app)
manager.add_command('server',Server)

@manager.shell
def make_shell_context():
    return dict(app=app,db=db,User=User,Post=Post)
if __name__=='__main__':
    manager.run()