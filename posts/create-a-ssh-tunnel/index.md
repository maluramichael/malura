---
title: "Create a ssh tunnel"
date: 2018-03-22
tags: ssh shell linux
---

```
#ssh -f user@remotehost -L localport:127.0.0.1:remoteport -N
$ ssh -f root@database -L 3307:127.0.0.1:3306 -N
```
Now it is possible to connect to a remote mysql database via the tunnel.
