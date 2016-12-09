__author__ = 'Ugrend'
import cherrypy
import configparser
import os

class Config:

    @staticmethod
    def get(section,option=None):
        try:
            if not cherrypy.request.app:
                # This should only be celery which will need the db connections
                config = configparser.ConfigParser()
                config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'server.conf'))
                if section and option:
                    return config.get(section, option).replace('\'',"")
                else:
                    return None
            if option:
                return cherrypy.request.app.config[section][option]
            else:
                return cherrypy.request.app.config[section]
        except KeyError:
            return None
        except configparser.NoOptionError:
            return None

    @staticmethod
    def set(section, option, value):
        if section not in cherrypy.request.app.config:
            cherrypy.request.app.config[section] = {}

        cherrypy.request.app.config[section][option] = value
