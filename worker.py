import os

import redis
from rq import Worker, Queue, Connection

"""
listening for a queue called 'default' and establishing a 
connection to the Redis server on localhost:6379
"""

listen = ['default']

#os.getenv returns env variable of key if it exists or 
#default if it doesn't exist where os.getenv(key, default=None)
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()