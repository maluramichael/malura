import datetime

import requests
import os
from diskcache import Cache
from tqdm import tqdm
from datetime import date

cache = Cache("_cache")

if 'NPMJS_TOKEN' not in os.environ:
    raise EnvironmentError('NPMJS_TOKEN environment variable not defined')

token = os.environ.get('NPMJS_TOKEN')

@cache.memoize(expire=60 * 60 * 24 * 7)
def get_downloads_for_package(name, today):
    year = date.today().year - 1

    result = {
        'last-year': 0,
        'this-year': 0,
    }
    data = requests.get(url=f'https://api.npmjs.org/downloads/range/{year}-01-01:{today}/{name}').json()
    result['this-year'] = sum(entry['downloads'] for entry in data['downloads'])
    data = requests.get(url=f'https://api.npmjs.org/downloads/range/last-year/{name}').json()
    result['last-year'] = sum(entry['downloads'] for entry in data['downloads'])

    return result


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_packages():
    resp = requests.get(url='https://registry.npmjs.org/-/user/maluramichael/package')
    data = resp.json()
    names = data.keys()

    packages = {}

    for name in tqdm(names, desc='Get npm download statistics'):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        packages[name] = get_downloads_for_package(name, today)

    return packages


def get_downloads_for_all_packages():
    packages = get_packages()
    downloads = {
        'last-year': 0,
        'this-year': 0
    }

    for key, package in packages.items():
        downloads['this-year'] += package['this-year']
        downloads['last-year'] += package['last-year']

    return downloads


def get_npm_infos():
    print('Get npmjs infos')
    packages = get_packages()
    return {
        'packages': packages,
        'downloads': get_downloads_for_all_packages()
    }
