---
title: "Import/Export mysql"
date: 2018-03-22
tags: mysql shell linux
---

With this snippets i can create a complete dump of a mysql database.

## dump
```
mysqldump --host="xyz" \
--user="xyz" --password="xyz" \
--default-character-set=latin1 \
--result-file="./dump.sql" \
--lock-tables --add-locks --create-options \
--extended-insert --add-drop-table --disable-keys \
databasename
```
## import
```
mysql --user="xyz" --password="xyz" \
--default-character-set=utf8 \
databasename < dump.sql
```
## better import
```
mysql -u root -p
mysql> SET names 'utf8'
mysql> SOURCE dump.sql
```
