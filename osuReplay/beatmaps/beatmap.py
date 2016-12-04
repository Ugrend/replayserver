__author__ = 'Ugrend'

from cachetools import LRUCache
from osuReplay.database.postgres import Sql
import os
from osuReplay.config import Config
from . import getbeatmaps
import time
from shutil import copyfile

class BeatmapLoader:
    def __init__(self):
        self.cache = LRUCache(maxsize=200)

    def load_beatmap(self, bmHash, expect_file=False):
        if bmHash in self.cache:
            return self.cache[bmHash]

        self.cache[bmHash] = {
            'hash': bmHash,
            'beatmap_id': None,
            'beatmap_set_id': None,
            'assets': [],
            'beatmap': ""
        }
        beatmap = self.cache[bmHash]
        beatmap_file = os.path.join(Config.get('General', 'beatmap_dir'), "%s.osu" % bmHash)
        if os.path.isfile(beatmap_file):
            sql = Sql()
            query = "SELECT beatmap_id, beatmap_set_id FROM beatmaps WHERE bmhash = %s"
            params = (bmHash,)
            beatmap_info = sql.execute_query(query, params)
            if len(beatmap_info) > 0:
                beatmap['beatmap_id'] = beatmap_info[0]['beatmap_id']
                beatmap['beatmap_set_id'] = beatmap_info[0]['beatmap_set_id']

            query = "SELECT ba.filename, a.filehash as md5sum FROM beatmap_to_assets ba " \
                    "JOIN assets a on a.id = ba.asset_id " \
                    "JOIN beatmaps b ON b.id = ba.beatmap_id " \
                    "WHERE b.bmhash = %s"
            beatmap['assets'] = sql.execute_query(query, params)
            with open(beatmap_file, 'rb') as f:
                beatmap['beatmap'] = f.read()
            return beatmap
        elif not expect_file:
            BeatmapLoader.download_beatmap(bmHash)
            return self.load_beatmap(bmHash, True)



    @staticmethod
    def download_beatmap(bmHash):
        map_info = getbeatmaps.get_map_info(bmHash)
        if len(map_info) > 0:
            map_data = map_info[0]
            map_data['bmhash'] = map_data.pop('file_hash')

            BeatmapLoader.insert_map_into_db(map_data)
            try_count = 0
            file = None
            while try_count < 10 and file is None:
                file = getbeatmaps.get_single_map(map_data['beatmap_id'])
                try_count += 1
                if not file:
                    time.sleep(0.5)
            if file:
                beatmap_file = os.path.join(Config.get('General', 'beatmap_dir'), "%s.osu" % bmHash)
                copyfile(file, beatmap_file)

    @staticmethod
    def insert_map_into_db(d):
        """
        Inserts map data into db
        :param d: dictionary of what to insert must match db colums or will fail
        :return:
        """
        sql = Sql()
        query = """INSERT INTO beatmaps (%s)VALUES (%s)
ON CONFLICT
    DO UPDATE SET
      beatmap_id=excluded.beatmap_id,
      beatmap_set_id=EXCLUDED.beatmap_set_id,
      approved=EXCLUDED.approved,
      approved_date=EXCLUDED.approved_date,
      last_update=EXCLUDED.last_update,
      favourite_count=EXCLUDED.favourite_count,
      playcount=EXCLUDED.playcount
      passcount=EXCLUDED.passcount"""
        columns = d.keys()
        params = (d, [d[c] for c in columns])
        sql.execute_query(query, params)