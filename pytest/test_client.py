import re
import pytest

from flask import url_for

from app import create_app
from app.models import db, User, Role, Post, Comment

@pytest.mark.usefixtures('client')
class TestFlaskClient(object):
    
    def test_home_page(self, client):
        response = client.get('/index', follow_redirects=True)
        # `get_data()` returns the response body as a byte array by default; passing
        # `as_text` returns a Unicode string that is much easier to work with.
        assert 'Login' in response.get_data(as_text=True)

    def test_register_and_login(self, client):
        # Register a new account
        response = client.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat',
        })
        assert response.status_code==302

        # Login with the new account
        response = client.post('/auth/login', data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        assert response.status_code==200
        assert re.search('Hello,\s+john', data).group() is not None
        assert 'You have not confirmed your email yet' in data

        # Send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = client.get(url_for('auth.confirm', token=token),
                              follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'You have confirmed your account' in data

        # Log out
        response = client.get('/auth/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        assert 'You have been logged out' in data