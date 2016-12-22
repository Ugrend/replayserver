from osuReplay.celeryloader import app
from osuReplay.config import Config
from osuReplay.database.postgres import Sql
from datetime import datetime, timedelta
import requests

osu_api = Config.get('General', 'osu_api_url') or "https://osu.ppy.sh/api"
api_key = Config.get('General', 'osu_api_key') or ""

def get_player_info(player_name_or_id):
    return requests.get(osu_api + "/get_user", params={'k': api_key, 'u': player_name_or_id}).json()


@app.task
def update_player_info(replay_id, replay):
    sql = Sql()
    query = "SELECT p.* FROM players p LEFT JOIN player_alias pa on pa.player_id = p.id WHERE p.player_name = %s OR pa.player_name = %s"
    params = (replay['playerName'], replay['playerName'])
    result = sql.execute_query(query, params)
    replaytime = datetime.fromtimestamp(replay['time_played'])
    player_info = get_player_info(replay['playerName'])
    if len(result) == 0:
        if len(player_info) > 0:
            query = """UPDATE replays SET player_id = player.id
                       FROM (INSERT INTO players (player_name, osu_user_id) VALUES (%s, %s) RETURNING id) as player
                       WHERE id = %s"""
            params = (replay['playerName'], player_info['user_id'], replay_id)
            sql.execute_query(query, params)

    if len(result) == 1:
        if len(player_info) > 0:
            pass







