from flask import Flask
import os
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #uses settings based on environment: staging, config, developement (local)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

print(os.environ['APP_SETTINGS'])

if __name__ == '__main__':
    app.run()
