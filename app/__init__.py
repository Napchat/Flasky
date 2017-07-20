from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_pagedown import PageDown


from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()

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

    from .models import db
    db.init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    from .blueprint import blueprint
    app.register_blueprint(blueprint)

    # url_prefix means that its url will be http://localhost:5000/auth/login
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from .main import main
    app.register_blueprint(main)

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    # Flask-SSLify intercept any requests sent to http:// interface and redirects 
    # them to https://.
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    return app