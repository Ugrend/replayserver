__author__ = 'Ugrend'

from cachetools import LRUCache
from osuReplay.database.postgres import Sql
import os
from osuReplay.config import Config
from . import getbeatmaps
import time
from shutil import copyfile
import base64
import hashlib
import threading
from psycopg2.extensions import AsIs


def get_md5_hash(filename):
    """
    This does not get the hash of the file itself but a hash of a b64 encoded version as this is what the website will use.
    :param filename:
    :return:
    """
    b64data = ""
    if filename.lower().endswith('jpeg') or filename.lower().endswith('jpg'):
        b64data = 'data:image/jpeg;base64,'
    if filename.lower().endswith('png'):
        b64data = "data:image/png;base64,"
    if filename.lower().endswith("wav"):
        b64data = "data:audio/wav;base64,"
    if filename.lower().endswith("mp3"):
        b64data = "data:audio/mpeg;base64,"

    with open(filename, 'rb') as f:
        b64data += base64.b64encode(f.read()).decode('utf-8')
    return hashlib.md5(b64data.encode('utf-8')).hexdigest()


def insert_map_into_db(d):
    """
    Inserts map data into db
    :param d: dictionary of what to insert must match db colums or will fail
    :return:
    """
    sql = Sql()
    query = """INSERT INTO beatmaps (%s) VALUES %s ON CONFLICT(bmhash) DO UPDATE SET bmhash=EXCLUDED.bmhash RETURNING id """
    columns = list(d.keys())
    params = (AsIs(','.join(columns)), tuple([d[c] for c in columns]))
    print(params)
    return sql.execute_query(query, params)[0]


def insert_assets(assets, bmID):
    sql = Sql()

    for asset in assets:
        try:
            trusted = asset['trusted']
        except KeyError:
            trusted = False

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
                    background = line.split(",")[2].replace('"',"").replace('\n',"").strip()

    return {'song': song, 'background': background}

def get_assets_for_set(beatmapset_id):
    """
    Get available assets for entire set, this is useful when adding a map that is part of a set that we already have saving downloading assets again
    :param beatmap_set_id:
    :return:
    """
    query = "SELECT ba.filename, a.filehash, ba.trusted as md5sum FROM beatmap_to_assets ba " \
            "JOIN assets a on a.id = ba.asset_id " \
            "JOIN beatmaps b ON b.id = ba.beatmap_id " \
            "WHERE b.beatmapset_id = %s"
    sql = Sql()
    return sql.execute_query(query, (beatmapset_id,))


def download_assets(beatmap_id, beatmap_source_id, beatmap_file, beatmap_set_id=None):
    required_files = get_filenames(beatmap_file)
    background = None
    song = None
    have_song = False
    have_background = False
    assets = []

    # First check if we have assets available from set
    if beatmap_set_id:
        db_assets = get_assets_for_set(beatmap_set_id)
        for result in db_assets:
            assets.append({'filename': result['filename'],
                           'md5sum': result['filehash'],
                           'trusted': result['trusted']})
    for asset in assets:
        if required_files['song'] == asset['filename']:
            have_song = True
        if required_files['background'] == asset['filename']:
            have_background = True

    try_count = 0
    while try_count < 10 and background is None and not have_background:
        background = getbeatmaps.get_map_background(beatmap_source_id)
        if not background:
            time.sleep(10)

    try_count = 0
    while try_count < 15 and song is None and not have_song:
        song = getbeatmaps.get_map_audio(beatmap_source_id)
        if not song:
            time.sleep(20)

    if background:
        background_hash = get_md5_hash(background)
        assets.append({'filename': required_files['background'], 'md5sum': background_hash, 'trusted': True})
    if song:
        song_hash = get_md5_hash(song)
        assets.append({'filename': required_files['song'], 'md5sum': song_hash, 'trusted': True})

    insert_assets(assets, beatmap_id)


def get_maps_for_set(beatmap_set_id):
    sql = Sql()
    query = "SELECT * FROM beatmaps WHERE beatmap_set_id = %s"
    params = (beatmap_set_id,)
    return sql.execute_query(query, params)


def download_assets_async(beatmap_id, beatmap_source_id, beatmap_file, beatmap_set_id=None):
    thread = threading.Thread(target=download_assets, args=(beatmap_id, beatmap_source_id, beatmap_file, beatmap_set_id))
    thread.start()


def download_beatmap(bmHash):
    map_info = getbeatmaps.get_map_info(bmHash)
    if len(map_info) > 0:
        map_data = map_info[0]
        map_data['bmhash'] = map_data.pop('file_md5')

        db_data = insert_map_into_db(map_data)
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
            download_assets_async(db_data['id'], map_data['beatmap_id'],beatmap_file,map_data['beatmapset_id'])





class BeatmapLoader:
    def __init__(self):
        self.cache = LRUCache(maxsize=200)

    def load_beatmap(self, bmHash, expect_file=False):
        asset_query = "SELECT ba.filename, a.filehash as md5sum FROM beatmap_to_assets ba " \
        "JOIN assets a on a.id = ba.asset_id " \
        "JOIN beatmaps b ON b.id = ba.beatmap_id " \
        "WHERE b.bmhash = %s"
        params = (bmHash,)
        if bmHash in self.cache:
            if len(self.cache[bmHash]['assets']) == 0:
                sql = Sql()
                self.cache[bmHash]['assets'] = sql.execute_query(asset_query, params)
                if len(self.cache[bmHash]['assets']) == 0:
                    # remove self from cache in hopes next time requested the assets will download
                    return self.cache.pop(bmHash)
            return self.cache[bmHash]

        self.cache[bmHash] = {
            'hash': bmHash,
            'beatmap_id': None,
            'beatmapset_id': None,
            'assets': [],
            'beatmap': ""
        }
        beatmap = self.cache[bmHash]
        beatmap_file = os.path.join(Config.get('General', 'beatmap_dir'), "%s.osu" % bmHash)
        if os.path.isfile(beatmap_file):
            sql = Sql()
            query = "SELECT id, beatmap_id, beatmapset_id FROM beatmaps WHERE bmhash = %s"

            beatmap_info = sql.execute_query(query, params)
            print(beatmap_info)
            if len(beatmap_info) > 0:
                beatmap['beatmap_id'] = beatmap_info[0]['beatmap_id']
                beatmap['beatmapset_id'] = beatmap_info[0]['beatmapset_id']


            beatmap['assets'] = sql.execute_query(asset_query, params)

            if len(beatmap['assets']) == 0 and not expect_file and len(beatmap_info) > 0:
                download_assets_async(beatmap_info[0]['id'], beatmap_info[0]['beatmap_id'], beatmap_file, beatmap_info[0]['beatmapset_id'])

            with open(beatmap_file, 'rb') as f:
                beatmap['beatmap'] = f.read().decode('utf-8')
            return beatmap
        elif not expect_file:
            # remove from cache as it will be empty
            self.cache.pop(bmHash)
            download_beatmap(bmHash)
            return self.load_beatmap(bmHash, True)



