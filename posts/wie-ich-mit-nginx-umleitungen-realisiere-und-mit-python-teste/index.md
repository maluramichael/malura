---
title: "Wie ich mit Nginx Umleitungen realisiere und mit Python teste"
date: 2020-02-11
tags: code python nginx http script
---

Ich brauchte für meinen Blog eine Möglichkeit leicht und schnell ganz viele Redirects zu definieren. In diesem Post möchte ich meine Lösung vorstellen.

Zuerst muss eine .map File erstellt werden. Jede Zeile stellt ein Redirect da und sollte folgendes Format haben `VON NACH;`. Wichtig ist es jede Zeile mit einem ; zu beenden.
```
/posts /blog;
/en/blog /blog;
/en/todo.html /blog/todo;
```
Die nginx Server Konfiguration sollte wie folgt aussehen.
```
map_hash_bucket_size 256;

map $uri $redirected_url {
  default "none";
  include /etc/nginx/redirects.map;
}

server {
  # ...
  if ($redirected_url != "none") {
    return 301 $redirected_url;
  }
  # ...
}
```
Dieses Python Script kann genutzt werden um die Redirects zu testen. Es lädt jede Zeile der `redirects.map`, führt einen Request darauf aus und überprüft ob richtig umgeleitet wurde.
```
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
```
