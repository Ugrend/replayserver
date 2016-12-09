__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success
from osuReplay.celeryloader import app


@json_output_all()
class Tasks:
    exposed = True

    def GET(self, task_id):
        return api_success(data=app.AsyncResult(task_id).state)
