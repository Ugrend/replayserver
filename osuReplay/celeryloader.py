from __future__ import absolute_import, unicode_literals
from celery import Celery

include=['osuReplay.beatmaps.beatmap',
         'osuReplay.players.player']

app = Celery('osuReplay', broker='pyamqp://guest@localhost//', backend='rpc://', include=include)
if __name__ == '__main__':
    app.start()