import re

import requests
from diskcache import Cache

cache = Cache("_cache")


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_games_count():
    data = requests.get(url='https://steamcommunity.com/id/leatherface90').text
    result = re.findall(r"(\d+) games owned", data, flags=re.DOTALL)

    if len(result) > 0:
        return int(result[0])

    return 0


def get_steam_infos():
    print('Get steam infos')
    return {
        'games': get_games_count()
    }
