import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app.models import db, User, Role, Permission, Follow, Comment
from app import create_app

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    # The `branch` argument enables branch coverage analysis, which, in addition
    # to tracking which lines of code execute, checks whether for every conditional
    # both the `True` and `False` cases have executed.
    COV = coverage.Coverage(branch=True, include='app/*')
    COV.start()


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, 
                Permission=Permission, Follow=Follow, Comment=Comment)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



@manager.command
def test(coverage=False):
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        
        # Restart the script with updated environment.
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@manager.command
def profile(length=25, profile_dir=None):
    '''Start the application under the code profiler.'''
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    '''Run deployment tasks.'''
    from flask_migrate import upgrade
    from app.models import Role, User

    # Migrate database to latest version
    upgrade()

    # Create user role
    Role.insert_roles()

    # Create self-follows for all users
    User.add_self_follows()

if __name__ == '__main__':
    manager.run()