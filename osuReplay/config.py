__author__ = 'Ugrend'
import cherrypy


class Config:

    @staticmethod
    def get(section,option=None):
        try:
            if option:
                return cherrypy.request.app.config[section][option]
            else:
                return cherrypy.request.app.config[section]
        except KeyError:
            return None

    @staticmethod
    def set(section, option, value):
        if section not in cherrypy.request.app.config:
            cherrypy.request.app.config[section] = {}

        cherrypy.request.app.config[section][option] = value

