import re

import requests
from diskcache import Cache

cache = Cache("_cache")


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_games_count():
    data = requests.get(url='https://steamcommunity.com/id/leatherface90').text
    # Try multiple patterns to find games count
    # Pattern 1: "1,066 games" (with comma)
    result = re.findall(r"([\d,]+)\s+games", data, flags=re.IGNORECASE)

    if len(result) > 0:
        # Remove commas and convert to int
        games_str = result[0].replace(',', '')
        return int(games_str)

    return 0


def get_steam_infos():
    print('Get steam infos')
    return {
        'games': get_games_count()
    }
