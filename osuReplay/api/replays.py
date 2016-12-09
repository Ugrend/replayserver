__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success
from cachetools import LRUCache
from hashids import Hashids
from osuReplay.config import Config
from osuReplay.database.postgres import Sql
import os
import base64
from osuReplay.replayparser import replay_parser
import hashlib
from _lzma import LZMAError
import traceback

@json_output_all()
class Replays:
    exposed = True

    def __init__(self):
        self.cache = LRUCache(maxsize=500)
        self.replayhash_cache = LRUCache(maxsize=1000)
        self.SALT = Config.get('General', 'salt')

    def GET(self, replay_id=None, beatmap_id=None, validate_only=False, limit=50):
        if limit > 100:
            limit = 100
        if replay_id is None and beatmap_id is None:
            return api_error("Either replay_id or beatmap_id must be set")
        replay = {}

        if replay_id:
            if len(replay_id) < 32:
                if replay_id in self.cache:
                    replay = self.cache[replay_id]
                else:
                    replay_db_id = Hashids(salt=self.SALT, min_length=5).decode(replay_id)
                    sql = Sql()
                    result = sql.execute_query("SELECT id, replayhash FROM replays WHERE id = %s", (replay_db_id,))
                    if len(result) > 0:
                        replay['id'] = result[0]['id']
                        replay['replayhash'] = result[0]['replayhash']
                    else:
                        if validate_only:
                            return False
                        return api_error("No such replay found")

                    replay_file = os.path.join(Config.get('General','replay_dir'),'%s.osr' % replay['replayhash'])
                    if os.path.isfile(replay_file):
                        with open(replay_file, 'rb') as f:
                            replay['data'] = base64.b64encode(f.read())
                    else:
                        # we have a replay in the DB that does not exist on disk, prob need to know about these
                        return api_error("No such replay found")

                self.cache[replay_id] = replay
                if validate_only:
                    return True
                return api_success(data=replay['data'].decode('utf-8'))
            else:
                # md5hash we will return the id only
                if replay_id in self.replayhash_cache:
                    return self.replayhash_cache[replay_id]
                sql = Sql()
                result = sql.execute_query("SELECT id,replayhash FROM replays WHERE replayhash = %s OR replay64hash = %s", (replay_id,replay_id))
                if len(result) > 0:
                    self.replayhash_cache[replay_id] = Hashids(salt=self.SALT, min_length=5).encode(result[0]['id'])
                    return self.replayhash_cache[replay_id]
                return False

        if beatmap_id:
            return api_error("Sorry not implemented yet")

    def POST(self, replay):
        data = replay.file.read()
        encoded = base64.b64encode(data)
        r = replay_parser.ReplayParser()

        try:
            r.load_replay(data)
            replayMd5 = hashlib.md5(data).hexdigest()
            replay64hash = hashlib.md5(encoded).hexdigest()
            sql = Sql()
            query = "INSERT into replays (replayhash,replay64hash, game_type, player_name, hit_300, hit_100, " \
                    "hit_50, hit_gekis, hit_katus, total_score, total_combo,total_misses, mods, time_played, bmhash)" \
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (replayhash) replayhash=EXCLUDED.replayhash RETURNING id"
            params = (
                replayMd5, replay64hash, r.type, r.playerName, r.h300, r.h100, r.h50, r.hGekis, r.hKatus, r.tScore, r.tCombo,
                r.hMisses, r.mods, r.time_played, r.bmMd5Hash
            )

            replay_id = sql.execute_query(query, params)
            hashid = Hashids(salt=self.SALT, min_length=5).encode(replay_id[0]['id'])
            with open(os.path.join(Config.get('General','replay_dir'),'%s.osr' % replayMd5), 'wb') as f:
                f.write(data)
            return api_success(data={'replay_hash': replayMd5, 'beatmap_hash': r.bmMd5Hash, 'replay_id': hashid})

        except (IndexError, LZMAError):
            traceback.print_exc()
            return api_error("Invalid or Corrupt replay File!")
