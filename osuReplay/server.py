__author__ = 'Ugrend'
import cherrypy
import os
from shutil import copyfile
from osuReplay.api.replays import Replays
from osuReplay.api.beatmaps import BeatMaps
from osuReplay.api.assets import Assets
from osuReplay.api.tasks import Tasks

if __name__ == '__main__':
    if not os.path.isfile("server.conf"):
        cherrypy.log("No server.conf found resorting to defaults")
        copyfile('server-default.conf', 'server.conf')
    cherrypy.config.update("server.conf")
    cherrypy.lib.cptools.proxy()
    cherrypy.tree.mount(Replays(), '/api/replays', 'server.conf')
    cherrypy.tree.mount(BeatMaps(), '/api/beatmaps', 'server.conf')
    cherrypy.tree.mount(Assets(), '/api/assets', 'server.conf')
    cherrypy.tree.mount(Tasks(), '/api/tasks', 'server.conf')
    cherrypy.engine.start()
    cherrypy.engine.block()
