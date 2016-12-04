__author__ = 'Ugrend'
import cherrypy

class Logger:

    @staticmethod
    def INFO(msg):
        cherrypy.log(msg)

    @staticmethod
    def WARN(msg):
        cherrypy.log(msg)

    @staticmethod
    def CRITICAL(msg):
        cherrypy.log(msg)

    @staticmethod
    def DEBUG(msg):
        cherrypy.log(msg)