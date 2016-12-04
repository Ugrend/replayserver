__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success


@json_output_all()
class Replays:
    exposed = True

    def GET(self):
        return True

    def PUT(self):
        return True

    def POST(self):
        return True

    def DELETE(self):
        return True

