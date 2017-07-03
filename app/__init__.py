from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()

# Flask-login initialization.
login_manager = LoginManager()

# sets to the endpoint for the login page.
login_manager.login_view = 'auth.login'

# session_protection is used to against user session tampering, with `strong`
# setting, Flask-Login will keep track of the client's IP address and brower
# agent and will log the user out if it detects a change.
login_manager.session_protection = 'strong'

def create_app(config_name):
    '''Application factory.'''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from app.models import db
    db.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from .blueprint import blueprint
    app.register_blueprint(blueprint)

    # url_prefix means that its url will be http://localhost:5000/auth/login
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    return app