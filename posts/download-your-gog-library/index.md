---
title: "How to download your GOG library"
date: 2018-09-01
tags: gog downloads linux
---

I wanted to backup all my games from gog. So I found this handy tool.

You need to get the lgogdownloader either from [github](https://github.com/Sude-/lgogdownloader) or via your package manager
```
$ lgogdownloader
# provide your email, password and code

$ lgogdownloader --language=de,en --update-cache

$ cd YOUR_DOWNLOAD_DIRECTORY

$ lgogdownloader --language=de,en --download \
  --subdir-game gamename%/%dlcname%/%platform% \
  --use-cache --save-serials
```
