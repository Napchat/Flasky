import os
import pytest

from app.models import User, db, Permission, Role
from app import create_app

@pytest.mark.usefixtures('app')
class TestUserModel(object):

    def test_password_setter(self):
        u = User(password='cat')
        assert u.password_hash is not None

    def test_no_password_getter(self):
        u = User(password='cat')
        with pytest.raises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        assert u.verify_password('cat') is True
        assert u.verify_password('dog') is False

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        assert u.password_hash != u2.password_hash

    def test_generate_token_are_different(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email='susan@example.com', username='susan', password='susan')
        token1 = u.generate_confirmation_token()
        token2 = u2.generate_confirmation_token()
        token3 = u.generate_reset_token()
        token4 = u2.generate_reset_token()
        assert token1 != token2
        assert token3 != token4
        assert token1 != token3

    def test_token_confirm(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email='susan@example.com', username='susan', password='susan')
        token = u.generate_confirmation_token()
        token2 = u.generate_reset_token()
        assert u.confirm(token) is True
        assert u2.confirm(token) is False
        assert u.reset_password(token2, 'cat') is True
        assert u2.reset_password(token2, 'dog') is True
        assert u.verify_password('cat') is True
        assert u2.verify_password('dog') is True

    def test_user_role(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        assert u.role.name == 'User'
        assert u2.role.name == 'Administrator'

    def test_user_can(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        assert u.can(Role.query.filter_by(name='User').first().permissions) is True
        assert u.can(Role.query.filter_by(name='Moderator').first().permissions) is False
        assert u.can(Permission.ADMINISTER) is False
        assert u2.can(Role.query.filter_by(name='User').first().permissions) is True
        assert u2.can(Role.query.filter_by(name='Moderator').first().permissions) is True
        assert u2.can(Permission.ADMINISTER) is True

    def test_user_is_administrator(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        assert u.is_administrator() is False
        assert u2.is_administrator() is True