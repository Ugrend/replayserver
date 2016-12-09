__author__ = 'Ugrend'
from .helpers import json_output_all, api_error, api_success
from osuReplay.config import Config
import os
import json
import re
from osuReplay.beatmaps.beatmap import BeatmapLoader, insert_map

@json_output_all()
class BeatMaps:
    exposed = True


    def __init__(self):
        self.BeatMaps = BeatmapLoader()

    def GET(self, bmhash, validate_only=False, assets_only=False):
        """
        Returns beatmap/required assets based on hash
        :param bmhash: md5sum of osu map
        :param validate_only: if flag is set to true we only check if we have the map, not send the map
        :return: beatmap or true/false
        """
        if re.match(r"([a-fA-F\d]{32})", bmhash):
            beatmap = self.BeatMaps.load_beatmap(bmhash)

            if not beatmap:
                return api_error("No beatmap found :(")

            if assets_only:
                 result = {
                    'hash': bmhash,
                    'beatmap_id': beatmap['beatmap_id'],
                    'beatmapset_id': beatmap['beatmapset_id'],
                     'assets': beatmap['assets']
                 }
                 return api_success(data=result)
            if validate_only:
                result = {
                    'hash': bmhash,
                    'beatmap_id': beatmap['beatmap_id'],
                    'beatmapset_id': beatmap['beatmapset_id']
                }
                return api_success(data=result)
            return api_success(data=beatmap)

        return api_error("No beatmap found :(")

    def PUT(self):
        return True

    def POST(self, beatmap, assets=None):
        if assets:
            assets = json.loads(assets)
        if assets and not isinstance(assets,list):
            return api_error("Assets must be in an array! eg: [{'filename': 'song.mp3', 'md5sum': '3018309812098301801284'}]", data=assets)

        return api_success(data=insert_map.delay(beatmap, assets).id)



