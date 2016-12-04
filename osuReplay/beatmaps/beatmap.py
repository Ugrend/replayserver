__author__ = 'Ugrend'

from cachetools import LRUCache
from osuReplay.database.postgres import Sql
import os
from osuReplay.config import Config
from . import getbeatmaps
import time
from shutil import copyfile


def get_md5_hash(filename):
    pass

def insert_map_into_db(d):
    """
    Inserts map data into db
    :param d: dictionary of what to insert must match db colums or will fail
    :return:
    """
    sql = Sql()
    query = """INSERT INTO beatmaps (%s) VALUES (%s) ON CONFLICT DO NOTHING"""
    columns = d.keys()
    params = (d, [d[c] for c in columns])
    sql.execute_query(query, params)


def download_beatmap(bmHash):
    map_info = getbeatmaps.get_map_info(bmHash)
    if len(map_info) > 0:
        map_data = map_info[0]
        map_data['bmhash'] = map_data.pop('file_hash')

        insert_map_into_db(map_data)
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


def insert_assets(assets, bmID, trusted=False):
    sql = Sql()
    for asset in assets:
        query = "INSERT INTO assets (filehash) VALUES (%s) ON CONFLICT(filehash) DO UPDATE SET filehash=EXCLUDED.filehash RETURNING id"
        params = (asset['md5sum'],)
        asset_id = sql.execute_query(query, params)[0]['id']
        if trusted:
            query = "INSERT INTO  beatmap_to_assets (beatmap_id, asset_id, trusted, filename) VALUES (%s,%s,TRUE,%s) \
                        ON CONFLICT ON CONSTRAINT beatmap_to_assets_beatmap_id_asset_id_key DO UPDATE SET trusted=EXCLUDED.trusted;"
        else:
            query = "INSERT INTO  beatmap_to_assets (beatmap_id, asset_id, trusted, filename) VALUES (%s,%s,FALSE,%s) \
                        ON CONFLICT ON CONSTRAINT beatmap_to_assets_beatmap_id_asset_id_key DO NOTHING"

        params = (bmID, asset_id, asset['filename'])
        sql.execute_query(query, params)


def get_filenames(beatmap_file):
    song = None
    background = None
    with open(beatmap_file, 'r') as f:
        contents = f.readlines()
        in_events = False
        for line in contents:
            if song and background:
                break
            if line.startswith('AudioFilename'):
                song = line.split('AudioFilename:')[1].strip()

            if line.startswith('[Events]'):
                in_events = True

            if in_events:
                if line.startswith("0"):
                    background = line.split(",")[2]

    return {'song': song, 'background': background}


def download_assets(beatmap_id, beatmap_source_id, beatmap_file):
    assets = get_filenames(beatmap_file)
    background = None
    song = None
    try_count = 0
    while try_count < 10 and background is None:
        background = getbeatmaps.get_map_background(beatmap_source_id)
        if not background:
            time.sleep(10)

    try_count = 0
    while try_count < 15 and song is None:
        song = getbeatmaps.get_map_audio(beatmap_source_id)
        if not song:
            time.sleep(20)



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
            download_beatmap(bmHash)
            return self.load_beatmap(bmHash, True)



