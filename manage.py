from flask_script import Manager,Server
from flask_migrate import Migrate,MigrateCommand
from app.models import User,Post,Tag,Comment,Role,Message
import os
from app import create_app,db,mail,search,socketio


app = create_app()
migrate=Migrate(app,db)
manager=Manager(app)
manager.add_command('server',Server)
manager.add_command('db',MigrateCommand)




@manager.shell
def make_shell_context():
    return dict(app=app,db=db,User=User,Post=Post,Tag=Tag,Comment=Comment,mail=mail,Role =Role,Message=Message)



if __name__=='__main__':
    manager.run()