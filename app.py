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
from rq import Queue
from rq.job import Job
from worker import conn
from flask import jsonify
import json

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS']) #uses settings based on environment: staging, config, developement (local)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #how is this inheriting from app?

#set up a Redis connection and initialize a queue based
#on that connection
q = Queue(connection=conn) 

from models import *
#why doesn't this work?: from models import Result. maybe bc of Python version?


def count_and_save_words(url):

    errors = []

    try:
        r = requests.get(url)
        #print(r.text) # print text of site to terminal
    except:
        errors.append("Unable to get URL. Please make sure it's valid and try again.")
        return {"error": errors} # why do we now return a dict?

    # text processing
    raw = BeautifulSoup(r.text).get_text()
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
        return result.id
    except:
        errors.append("Unable to add item to database.")
        return {"error" : errors}

#requests is a library for sending external HTTP GET requests. Will be used to grab the specific user-provided URL
#request is a flask object used to GET and POST requests within the Flask app
@app.route('/', methods=['GET', 'POST'])
def index():        
    return render_template('index.html')

#find out why these functions don't have to be called. automatically called from decorator?
@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    if 'http://' not in url[:7] and 'https://' not in url[:8]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
        )
    # return created job id
    return job.get_id()

@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:20]
        return jsonify(results)
    else:
        return "Nay!", 202


"""
@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)
"""
#print(os.environ['APP_SETTINGS']) #used to test different env-based settings

if __name__ == '__main__':
    app.run()
