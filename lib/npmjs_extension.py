import datetime

import requests
from github import Github
import os
from diskcache import Cache

cache = Cache("_cache")
token = os.environ.get('NPMJS_TOKEN')


@cache.memoize()
def get_downloads_for_package(name, today):
    year = 2021

    result = {
        'last-year': 0,
        'this-year': 0,
    }
    data = requests.get(url=f'https://api.npmjs.org/downloads/range/{year}-01-01:{today}/{name}').json()
    result['this-year'] = sum(entry['downloads'] for entry in data['downloads'])
    data = requests.get(url=f'https://api.npmjs.org/downloads/range/last-year/{name}').json()
    result['last-year'] = sum(entry['downloads'] for entry in data['downloads'])

    return result


@cache.memoize()
def get_packages():
    resp = requests.get(url='https://registry.npmjs.org/-/user/maluramichael/package')
    data = resp.json()
    names = data.keys()

    packages = {}

    for name in names:
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
    packages = get_packages()
    return {
        'packages': packages,
        'downloads': get_downloads_for_all_packages()
    }
