import os
import logging
import iren
import requests
import json
import threading
from flask import Flask, request, send_file, Response, jsonify
from flask_restx import Api, Resource, reqparse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from flask_caching import Cache

logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

executors = {
    'default': ThreadPoolExecutor(16),
    'processpool': ProcessPoolExecutor(4)
}

sched = BackgroundScheduler(timezone='Europe/Rome', executors=executors)


app = Flask(__name__)
config = {    
    "CACHE_TYPE" : os.environ['CACHE_TYPE'],
    "CACHE_REDIS_HOST" : os.environ['CACHE_REDIS_HOST'],
    "CACHE_REDIS_PORT" : os.environ['CACHE_REDIS_PORT'],
    "CACHE_REDIS_DB" : os.environ['CACHE_REDIS_DB'],
    "CACHE_REDIS_URL" : os.environ['CACHE_REDIS_URL'],
    "CACHE_DEFAULT_TIMEOUT" : os.environ['CACHE_DEFAULT_TIMEOUT']
}

app.config.from_mapping(config)
cache = Cache(app)
api = Api(app)

nsiren = api.namespace('iren', 'Iren APIs')

@nsiren.route('/login')
class IrenLoginClass(Resource):
  @cache.cached(timeout=60000, query_string=True)
  def get(self):
    return jsonify(iren.login())

@nsiren.route('/bollette')
class IrenBolletteClass(Resource):
  @cache.cached(timeout=60000, query_string=True)
  def get(self):
    return jsonify(iren.get_bollette())

sched.add_job(iren.fatture_to_calendar, 'interval', hours=24, id="login")

if __name__ == '__main__':
  sched.start()
  cache.init_app(app)
  app.run()
