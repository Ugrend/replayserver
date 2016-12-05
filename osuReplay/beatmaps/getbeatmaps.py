__author__ = 'Ugrend'
import requests
from osuReplay.config import Config
import os


def get_map_info(h):
    osu_api = Config.get('General', 'osu_api_url') or "https://osu.ppy.sh/api"
    api_key = Config.get('General', 'osu_api_key') or ""
    return requests.get(osu_api + "/get_beatmaps", params={'k': api_key, 'h':h}).json()


def download_set(set_id):
    tmpdir = Config.get('General', 'tmp_dir')
    download_url = Config.get('AssetServer', 'asset_source')
    filename = os.path.join(tmpdir, "%s.osz" % set_id)
    if os.path.isfile(filename):
        return filename
    bc = requests.get(download_url + "s/%s" % set_id, stream=True)
    with open(filename, 'wb') as f:
        for chunk in bc.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    return filename


def get_single_map(map_id):
    tmpdir = Config.get('General', 'tmp_dir')
    download_url = Config.get('AssetServer', 'asset_source')
    filename = os.path.join(tmpdir, "%s.osu" % map_id)
    if os.path.isfile(filename) and not os.path.isfile(filename + '.lock'):
        return filename

    print(os.path.isfile(filename + '.lock'))
    if not os.path.isfile(filename + '.lock'):
        print(filename)
        open(filename + '.lock', 'w').close()
        bc = requests.get(download_url + "b/%s" % map_id, stream=True)
        with open(filename, 'wb') as f:
            for chunk in bc.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        os.remove(filename + '.lock')
        return filename


def get_map_background(map_id):
    tmpdir = Config.get('General', 'tmp_dir')
    download_url = Config.get('AssetServer', 'asset_source')
    filename = os.path.join(tmpdir, "%s.jpg" % map_id)
    if os.path.isfile(filename) and not os.path.isfile(filename + '.lock'):
        return filename
    if not os.path.isfile(filename + '.lock'):
        open(filename + '.lock', 'w').close()
        bc = requests.get(download_url + "i/%s" % map_id, stream=True)
        with open(filename, 'wb') as f:
            for chunk in bc.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        os.remove(filename + '.lock')
        return filename


def get_map_audio(map_id):
    tmpdir = Config.get('General', 'tmp_dir')
    download_url = Config.get('AssetServer', 'asset_source')
    filename = os.path.join(tmpdir, "%s.mp3" % map_id)
    if os.path.isfile(filename) and not os.path.isfile(filename + '.lock'):
        return filename

    if not os.path.isfile(filename + '.lock'):
        open(filename + '.lock', 'w').close()
        bc = requests.get(download_url + "a/%s" % map_id, stream=True)
        with open(filename, 'wb') as f:
            for chunk in bc.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
        os.remove(filename + '.lock')
        return filename
