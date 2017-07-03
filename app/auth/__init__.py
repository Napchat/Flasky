from flask import Flask

auth = Blueprint('auth', __name__)

from . import views