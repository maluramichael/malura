import re

import requests
from diskcache import Cache

from lib.html_parser import HtmlStripper

cache = Cache("_cache")


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_games_count():
    data = requests.get(url='https://www.gog.com/u/maluramichael').text
    stripper = HtmlStripper()
    stripper.feed(data)
    text = stripper.text.getvalue()
    result = re.findall(r"\"games_owned\":(\d+)", text, flags=re.DOTALL)

    if len(result) > 0:
        return int(result[0])

    return 0


def get_gog_infos():
    print('Get gog infos')
    return {
        'games': get_games_count()
    }
