from datetime import datetime
import hashlib

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from markdown import markdown
import bleach

from . import login_manager

db = SQLAlchemy()

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class User(db.Model, UserMixin):
    '''The ``UserMixin`` implements four function(property) that Flask_Login needs.
    meth: is_authenticated(); is_active(); is_anonymous; get_id()
    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_name = db.Column(db.String(64), db.ForeignKey('roles.name'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # `datatime.utcnow` is missing the () at the end. This is because the `default` argument
    # to `db.Column()` can take a function as a default value, so each time a default value
    # needs to be generated the function is invoked to produce it. 
    # 传入的是函数，而不是函数的结果
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permission):
        return self.role is not None and (self.role.permissions & permission) == permission

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    '''When the user is not logged_in, `current_user` is set to the object of this class.
    This will enable the application to freely call `current_user.can()` and `current_user.is_administrator()`
    without having to check whether the user is logged in first.
    '''
    def can(self, permission):
        return False

    def is_administrator(self):
        return False

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # the `default` field should be set to True for only one role and False for all the others.
    # the role marked as default will be the one assigned to new users upon registration.
    default = db.Column(db.Boolean, default=False, index=True)

    # this field is an integer that will be used as bit flags.
    # each task will be assigned a bit position, and for each role the tasks that are allowed for that
    # role will have their bits set to 1.
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        '''Update and insert roles.'''
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        '''The function renders the HTML version of the body and stores
        it in body_html, effectively making the conversion of the Mark-down
        text to HTML fully automatic.

        the actual conversion is donw in three steps in `meth: target_body_html`:

            First, the `markdown()` function does an initial conversion to HTML.

            Second, the resualt from the first step is passed to `clean()`, along
        with the list of approved HTML tags. The `clean()` function removes any tags
        not on the white list.

            Finally, function `linkify()` provided by Bleach converts any URLs written
        in plain text into proper <a> links. This last step is necessary because automatic
        link generation is not officially in the Markdown specification. PageDown supports 
        it as an extension. 
        '''
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'en', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']

        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))

@login_manager.user_loader
def load_user(user_id):
    '''Flask_login requires the app to set up a callback function that loads a user,
    given the identifier. The return value of the function must be the user object if available.
    '''
    return User.query.get(int(user_id))

# The `on_changed_body` function is registered as a listener of SQLAlchemy's
# 'set' event for `body`, which means that it will be automatically invoked
# whenever the `body` field on any instance of the class is set to a new value.
db.event.listen(Post.body, 'set', Post.on_changed_body)