__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success
from osuReplay.config import Config
import os
import re
from cachetools import LRUCache
from osuReplay.database.postgres import Sql


@json_output_all()
class BeatMaps:
    exposed = True

    cache = LRUCache(maxsize=200)

    def GET(self, bmhash, validate_only=False):
        """
        Returns beatmap/required assets based on hash
        :param bmhash: md5sum of osu map
        :param validate_only: if flag is set to true we only check if we have the map, not send the map
        :return: beatmap or true/false
        """

        if re.match(r"([a-fA-F\d]{32})", bmhash):
            beatmap = None
            if bmhash in self.cache:
                beatmap = self.cache[bmhash]

            beatmap_file = os.path.join(Config.get('General', 'beatmap_dir'), "%s.osu" % bmhash)
            if not beatmap and os.path.isfile(beatmap_file):
                self.cache[bmhash] = {
                    'hash': bmhash,
                    'beatmap_id': None,
                    'beatmap_set_id': None,
                    'assets': [],
                    'beatmap': ""
                }
                beatmap = self.cache[bmhash]
                sql = Sql()
                query = "SELECT beatmap_id, beatmap_set_id FROM beatmaps WHERE bmhash = %s"
                params = (bmhash,)
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
            else:
                pass


            if not beatmap:
                return api_error("No beatmap found :(")

            if validate_only:
                result = {
                    'hash': bmhash,
                    'beatmap_id': beatmap['beatmap_id'],
                    'beatmap_set_id': beatmap['beatmap_set_id']
                }
                return api_success(data=result)
            return api_success(data=beatmap)




        return api_error("No beatmap found :(")

    def PUT(self):
        return True

    def POST(self):
        return True

    def DELETE(self):
        return True

