import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter # a container that keeps track of how many times equivalent values are added. returns a dictionary
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #uses settings based on environment: staging, config, developement (local)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #how is this inheriting from app?

from models import *
#why doesn't this work?: from models import Result. maybe bc of Python version?

#requests is a library for sending external HTTP GET requests. Will be used to grab the specific user-provided URL
#request is a flask object used to GET and POST requests within the Flask app
@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        #get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
            #print(r.text) # print text of site to terminal
        except:
            errors.append("Unable to get URL. Please make sure it's valid and try again.")
    #if request is a 'GET' rather than 'POST', we just return the rendered template
            return render_template('index.html', errors=errors, results=results)
        if r:
            # text processing
            raw = BeautifulSoup(r.text, 'html.parser').get_text()
            nltk.data.path.append('/home/nlibassi/flask-by-example/nltk_data/') # set the path 
            tokens = nltk.word_tokenize(raw) # returns list, same as split using space?
            text = nltk.Text(tokens)
            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words) #Counter imported from collections, returns dict showing how many times each word is used            
            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops and len(w) < 12] # lower() converts string to lower case
            #print('NO STOP WORDS is {}'.format(no_stop_words))            
            no_stop_words_count = Counter(no_stop_words)
            # save the results, sorting according to frequency
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:20] #display only first 20 words
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")    
    return render_template('index.html', errors=errors, results=results)
"""
@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)
"""
#print(os.environ['APP_SETTINGS']) #used to test different env-based settings

if __name__ == '__main__':
    app.run()
