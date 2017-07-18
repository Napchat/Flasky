from flask_httpauth import HTTPBasicAuth
from flask import g, jsonify

from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

# RESTful API are stateless, it doesn't use Cookie and Session, 
# So Flask-Login is not able to handle user credentials, instead 
# Flask-HttpAuth is used.
auth = HTTPBasicAuth()

@api.before_request
@auth.login_required
def before_request():
    '''The `auth.login_required` will apply to every request.'''
    if (not g.current_user.is_anonymous and
            not g.current_user.confirmed):
        return forbidden('Unconfirmed account')

@auth.verify_password
def verify_password(email_or_token, password):
    # first, check email and token
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True

    # if password is not supllied, the only way to check the user 
    # is through token.
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.curren_user is not None

    # if password is supllied, then check user's email and password.
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.route('/token')
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
