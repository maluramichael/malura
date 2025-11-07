---
title: "Noch mehr Docker Container"
date: 2019-08-22
tags: docker gogs jira joomla
---

Wie versprochen gibt es wieder ein paar Docker Container aus meinem Homelab.

## Gogs
```
version: '2'
services:
    postgres:
      image: postgres:9.5
      restart: always
      environment:
       - "POSTGRES_USER=gogs"
       - "POSTGRES_PASSWORD=gogs"
       - "POSTGRES_DB=gogs"
      volumes:
       - "db-data:/var/lib/postgresql/data"
      networks:
       - gogs
    gogs:
      image: gogs/gogs:latest
      restart: always
      ports:
       - "3000:3000"
      links:
       - postgres
      environment:
       - "RUN_CROND=true"
      networks:
       - gogs
      volumes:
       - "gogs-data:/data"
      depends_on:
       - postgres

networks:
    gogs:
      driver: bridge

volumes:
    db-data:
      driver: local
    gogs-data:
      driver: local
```
## Jira
```
version: '3.1'
services:
  jira:
    image: cptactionhank/atlassian-jira
    restart: always
    ports:
      - 8777:8080
    links:
      - database
    networks:
      - jira
    volumes:
      - "jira-home-data:/var/atlassian/jira"
      - "jira-install-data:/opt/atlassian/jira"
    depends_on:
      - database

  database:
    image: postgres:9.5
    restart: always
    environment:
      - "POSTGRES_USER=jira"
      - "POSTGRES_PASSWORD=jira"
      - "POSTGRES_DB=jira"
    volumes:
      - "db-data:/var/lib/postgresql/data"
    networks:
      - jira

networks:
  jira:
    driver: bridge

volumes:
  db-data:
    driver: local
  jira-home-data:
    driver: local
  jira-install-data:
    driver: local
```
## Joomla
```
version: '3.1'

services:
  joomla:
    image: joomla
    restart: always
    links:
      - joomladb
    ports:
      - 8080:80
    environment:
      JOOMLA_DB_HOST: joomladb
      JOOMLA_DB_PASSWORD: joomla

  joomladb:
    image: mysql:5.6
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: joomla
```
