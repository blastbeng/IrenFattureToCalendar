import os
import logging
import iren
import requests
import json
from flask import Flask, request, send_file, Response, jsonify
from flask_apscheduler import APScheduler
from flask_restx import Api, Resource, reqparse

class Config:
    SCHEDULER_API_ENABLED = True

logging.basicConfig(level=logging.ERROR)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


app = Flask(__name__)
app.config.from_object(Config())
api = Api(app)

scheduler = APScheduler()

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
  scheduler.init_app(app)
  scheduler.start()

@scheduler.task('interval', id='fatture_to_calendar', hours=int(os.environ['SCHEDULER_TIME']), misfire_grace_time=900)
def fatture_to_calendar():
    iren.fatture_to_calendar()

if __name__ == '__main__':
  app.run()
