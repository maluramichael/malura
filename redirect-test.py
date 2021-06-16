import requests
from urllib.parse import urljoin

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

base = 'https://malura.de'

redirect_count = 0
redirect_success_count = 0

with open('redirects.map') as fp:
    for cnt, line in enumerate(fp):
        redirect_count += 1
        [url, redirect] = [urljoin(base, chunk.strip().replace(';', '')) for chunk in line.split(' ')]
        r = requests.get(url, allow_redirects=False)

        redirected_location = r.headers['Location']
        if redirected_location != redirect:
            print("{} -> {} = {}".format(url, redirect, redirected_location))
        else:
            redirect_success_count += 1

if redirect_success_count != redirect_count:
    print(f"{bcolors.FAIL}{redirect_count - redirect_success_count} redirects didnt work{bcolors.ENDC}")
