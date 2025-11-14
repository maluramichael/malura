---
title: "How to remove sound distortions in debian"
date: 2018-08-30
tags: debian linux shell audio daemon help fix
---

When using Debian, I sometimes hear pretty bad distortions, lags and cracks while listening to spotify or playing games.
The following settings helped me fix this issue.
```
$ sudo nano /etc/pulse/daemon.conf

# search for ; default-fragment-size-msec
# remove the ; and set its value to something below 50
# for me it's working with 5
# save, quit and restart pulseaudio

pulseaudio -k;pulseaudio --start
```
