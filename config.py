import os

class Config(object):
    DEBUG = False
    TESTING = False
    basedir = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URI = ''
    SECRET_KEY = ''

class ProductionConfig(Config):
    DATABASE_URI = ''

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True