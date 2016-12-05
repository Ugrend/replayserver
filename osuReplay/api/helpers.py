__author__ = 'Ugrend'
from datetime import datetime
import json
import cherrypy
from osuReplay.config import Config
def json_serial_datetime(obj):
    """
    Converts a datetime object to a string
    :param obj: datetime object
    :return:
    """
    if isinstance(obj, datetime):
        serial = obj.strftime('%d/%m/%Y - %H:%M:%S')
        return serial


def json_output(func):
    def json_output_(*args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*" #TODO: TURN THIS SHIT OFF BEFORE PROD
        return json.dumps(func(*args, **kwargs), default=json_serial_datetime, indent=5).encode('utf-8')

    return json_output_


def json_output_all():
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                if attr.isupper():
                    setattr(cls, attr, json_output(getattr(cls, attr)))
        return cls
    return decorate


def restrict_ip(func):
    def restrict_ip_(*args, **kwargs):
        if cherrypy.request.remote.ip in Config.get('AssetServer', 'allowed_ips'):
            return func(*args, **kwargs)
        else:
            raise cherrypy.HTTPError("403 Forbidden", "You are not allowed to access this resource.")
    return restrict_ip_

def api_success(msg=None, data=None):
    return {'status': 'success', 'msg': msg, 'data': data}


def api_error(msg=None, data=None):
    return {'status': 'error', 'msg': msg, 'data': data}

