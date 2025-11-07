---
title: "Bash one liner part 1"
date: 2021-06-01
tags: bash ssh tips
---

## Download httpd log files from multiple servers.

My `.ssh/servers` config looks something like this.
```
Host frontend
    HostName xxx
    IdentityFile xxx
    ....
```
```
for server in $(egrep -i '^Host\s.+' ~/.ssh/servers | awk '{print $2}'); do
    mkdir -p $server
    scp -r $server:/var/log/httpd $server/
    scp -r $server:/var/app/current/var/log $server/
done
```
## Find unique errors in all logs.

My log file looks like this: `[2021-05-31 09:14:32] request.ERROR: Uncaught PHP Exception Symfony\...`

I had to remove the time and date, sort the lines, remove all whitespaces at the beginning of the line and pipe it through the uniq command.
```
cat $(find . -name "prod.error.log" | xargs) | awk '{$1=""; $2=""; print$0}' | tr -d ' ' | sort | uniq > errors.log
```
