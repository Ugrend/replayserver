__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success, restrict_ip

@json_output_all()
class Assets:
    exposed = True

    @restrict_ip
    def GET(self):
        return True

    @restrict_ip
    def PUT(self):
        return True

    @restrict_ip
    def POST(self):
        return True

    @restrict_ip
    def DELETE(self):
        return True