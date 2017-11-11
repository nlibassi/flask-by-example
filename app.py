from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #uses settings based on environment: staging, config, developement (local)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #how is this inheriting from app?

from models import Result

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

#print(os.environ['APP_SETTINGS']) #used to test different env-based settings

if __name__ == '__main__':
    app.run()
