import os
import logging
import iren
import requests
import json
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
api = Api(app)

nsiren = api.namespace('iren', 'Iren APIs')

@nsiren.route('/login')
class IrenLoginClass(Resource):
  def get(self):
    return jsonify(iren.login())

@nsiren.route('/bollette')
class IrenBolletteClass(Resource):
  def get(self):
    return jsonify(iren.get_bollette())


if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
  iren.create_empty_tables()
  #iren.fatture_to_calendar()
  sched.add_job(iren.fatture_to_calendar, 'interval', hours=int(os.environ['SCHEDULER_TIME']), id="login")

if __name__ == '__main__':
  sched.start()
  cache.init_app(app)
  app.run()
