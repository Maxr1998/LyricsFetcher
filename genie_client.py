import json
from json.decoder import JSONDecodeError
from urllib.parse import unquote

import requests

from lyrics import Lyrics

GENIE_ALBUM_API_URL = 'https://app.genie.co.kr/song/j_AlbumSongList.json?axnm={album_id:d}'
GENIE_LYRICS_API_URL = 'https://dn.genie.co.kr/app/purchase/get_msl.asp?songid={song_id:d}&callback=GenieCallback'
GENIE_STREAM_INFO_API_URL = 'https://stm.genie.co.kr/player/j_StmInfo.json?xgnm={song_id:d}'

CURL_USER_AGENT = 'curl/8.7.1'  # for whatever reason, this works, but the python-requests UA doesn't


class GenieSong:
    def __init__(self, song_id: int, song_name: str):
        self.song_id = song_id
        self.song_name = song_name


def fetch_genie_album_song_ids(album_id: int) -> list[GenieSong] | None:
    response = requests.get(GENIE_ALBUM_API_URL.format(album_id=album_id),
                            headers={'User-Agent': CURL_USER_AGENT})
    try:
        response_json = response.json()
    except JSONDecodeError:
        return None

    try:
        songs = list(response_json['DATA1']['DATA'])
        songs = sorted(songs, key=lambda x: x['ROWNUM'])
    except KeyError:
        return None

    # Extract songs
    result = []

    for song in songs:
        song_id = song.get('SONG_ID')
        song_name = song.get('SONG_NAME')

        if song_id is None or song_name is None:
            return None

        try:
            song_id = int(song_id)
        except ValueError:
            return None

        result.append(GenieSong(song_id=song_id, song_name=unquote(song_name)))

    return result


def fetch_lyrics(song_id: int) -> Lyrics | None:
    response = requests.get(GENIE_LYRICS_API_URL.format(song_id=song_id),
                            headers={'User-Agent': CURL_USER_AGENT})

    response_text = response.text
    if response_text.startswith('GenieCallback('):
        # We (probably) got timed lyrics
        response_text = response.text.removeprefix('GenieCallback(').removesuffix(');')
        try:
            raw_lyrics = json.loads(response_text)
        except JSONDecodeError:
            return None

        return Lyrics.timed(raw_lyrics)
    else:
        # Fall back to static lyrics
        response = requests.get(GENIE_STREAM_INFO_API_URL.format(song_id=song_id),
                                headers={'User-Agent': CURL_USER_AGENT})
        try:
            response_json = response.json()
        except JSONDecodeError:
            return None

        try:
            raw_lyrics = response_json['DataSet']['DATA'][0]['LYRICS']
        except KeyError:
            return None

        return Lyrics.static(unquote(raw_lyrics).split('<br>'))
