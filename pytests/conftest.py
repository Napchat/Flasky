'''Defines fixtures available to all tests.
https://docs.pytest.org/en/latest/fixture.html?highlight=fixture
'''

import pytest
import os

from app import create_app
from app.models import db, User, Post, Comment, Role

@pytest.fixture()
def app(request):
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    Role.insert_roles()

    def teardown():
        db.session.remove()
        db.drop_all()
        app_context.pop()

    request.addfinalizer(teardown)

    return app

@pytest.fixture()
def client(request):
    app = create_app('testing')
    test_request_context = app.test_request_context()
    test_request_context.push()
    db.create_all()
    Role.insert_roles()
    client = app.test_client(use_cookies=True)

    def teardown():
        db.session.remove()
        db.drop_all()
        test_request_context.pop()

    request.addfinalizer(teardown)

    return client