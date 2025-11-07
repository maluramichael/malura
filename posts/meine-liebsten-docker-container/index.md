---
title: "Meine liebsten Docker Container"
date: 2019-01-17
tags: docker deluge plex rss
---

Die folgenden Docker Container laufen aktuell in meinem Homelab.

## Deluge

Deluge ist ein Torrent Server. Ich lade meine Linux ISOs am liebsten ueber Torrent und moechte der Community natuerlich auch etwas zurueck geben.

Darum seede ich meine lieblings ISOs von meinem Homeserver aus in die weite Welt hinaus.
```
version: "2"
services:
  deluge:
    image: linuxserver/deluge
    container_name: deluge
    environment:
      - PUID=1002
      - PGID=1003
      - TZ=Europe/London
    ports:
      - "8112:8112"
      - "58846:58846"
      - "58946:58946"
      - "58946:58946/udp"
    volumes:
      - /srv/dev-disk-by-label-tank/torrent/config:/config
      - /srv/dev-disk-by-label-tank/torrent/downloads:/downloads
    mem_limit: 2048m
    restart: unless-stopped
```
## Plex

Natuerlich darf die Home-Version von Netflix nicht fehlen
```
version: "3"
services:
  plex:
    container_name: plex
    restart: always
    image: plexinc/pms-docker
    ports:
      - "32400:32400"
      - "1900:1900"
      - "3005:3005"
      - "5353:5353"
      - "8324:8324"
      - "32410:32410"
      - "32412:32412"
      - "32413:32413"
      - "32414:32414"
      - "32469:32469"
    volumes:
      - /srv/dev-disk-by-label-tank/docker/plex/config:/config
      - /srv/dev-disk-by-label-tank/docker/plex/transcode:/transcode
      - /srv/dev-disk-by-label-tank/docker/plex/shared:/shared
      - /srv/dev-disk-by-label-tank/media:/media
    environment:
      - TZ=Europe/London
      - HOSTNAME="Docker Plex"
      - PLEX_UID=121
      - PLEX_GID=1001
      - PLEX_CLAIM=xxxxxxxxxxxxxxx
      - ADVERTISE_IP="https://192.168.178.100:32400/"
```
## RSS Reader
```
version: "3"
services:
  rss:
    restart: always
    image: linuxserver/tt-rss
    ports:
      - "7800:80"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /tank/docker/tt-rss/config:/config
      - /tank/docker/tt-rss/data:/var/lib/postgresql/data
    environment:
      - TZ=Europe/Berlin
    links:
      - db
  db:
    image: postgres
    restart: always
    environment:
      POSTGRES_PASSWORD: tt-rss
```
