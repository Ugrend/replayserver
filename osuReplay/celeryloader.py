from __future__ import absolute_import, unicode_literals
from celery import Celery
app = Celery('osuReplay', broker='pyamqp://guest@localhost//', backend='rpc://', include=['osuReplay.beatmaps.beatmap'])
if __name__ == '__main__':
    app.start()