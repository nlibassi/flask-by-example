import os

"""
different classes for different configurations allows us to use environment variables based on 
the environment - local, staging, production, etc
"""
basedir = os.path.abspath(os.path.dirname(__file__)) #returns directory name where this file (script) is located. 
#If directory structure changes, basedir will change as well. abspath 'Return a normalized absolutized version of the pathname path.'

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True #look up
    SECRET_KEY = b'\x1d2\xb7<\x1c\x1a/\xc23\xe7F\xa0\xe0\xdd\x16<\x95\x8c\xe7\xd2\x87\xf6\xa9}' #secret key for flask-by-example app
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']  #db url is also env-based

class ProductionConfig(Config):
    DEBUG = False #why does this need to be set? In case I later change it in Config class?

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

