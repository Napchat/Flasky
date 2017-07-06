import unittest
import os

from app.models import User, db, Permission, Role
from app import create_app

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_generate_token_are_different(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email='susan@example.com', username='susan', password='susan')
        token1 = u.generate_confirmation_token()
        token2 = u2.generate_confirmation_token()
        token3 = u.generate_reset_token()
        token4 = u2.generate_reset_token()
        self.assertNotEqual(token1, token2)
        self.assertNotEqual(token3, token4)
        self.assertNotEqual(token1, token3)

    def test_token_confirm(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email='susan@example.com', username='susan', password='susan')
        token = u.generate_confirmation_token()
        token2 = u.generate_reset_token()
        self.assertTrue(u.confirm(token))
        self.assertFalse(u2.confirm(token))
        self.assertTrue(u.reset_password(token2, 'cat'))
        self.assertTrue(u2.reset_password(token2, 'dog'))
        self.assertTrue(u.verify_password('cat'))
        self.assertTrue(u2.verify_password('dog'))

    def test_user_role(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        self.assertEqual(u.role.name, 'User')
        self.assertEqual(u2.role.name, 'Administrator')

    def test_user_can(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        self.assertTrue(u.can(Role.query.filter_by(name='User').first().permissions))
        self.assertFalse(u.can(Role.query.filter_by(name='Moderator').first().permissions))
        self.assertFalse(u.can(Permission.ADMINISTER))
        self.assertTrue(u2.can(Role.query.filter_by(name='User').first().permissions))
        self.assertTrue(u2.can(Role.query.filter_by(name='Moderator').first().permissions))
        self.assertTrue(u2.can(Permission.ADMINISTER))

    def test_user_is_administrator(self):
        u = User(email='john@example.com', username='john', password='john')
        u2 = User(email=os.environ.get('ADMIN'), username='susan', password='susan')
        self.assertFalse(u.is_administrator())
        self.assertTrue(u2.is_administrator())