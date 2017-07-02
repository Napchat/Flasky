import os
from app import create_app
from flask_script import Manager, Shell
import config

app = create_app(config.Config)
manager = Manager(app)

def make_shell_context():
    pass

manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()