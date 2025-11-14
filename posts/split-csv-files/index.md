---
title: "Split a CSV file"
date: 2018-03-26
tags: csv linux shell
---

I needed to split a csv with 14k entries in multiple files because the import on one of our servers would crash when i try to import all at once.
```
# split -l lines file_to_split output/
$ split -l 4000 export.csv export/venues
$ ls venues
venuesaa venuesab venuesac venuesad
$ cd export

# append .cvs extension to every file
$ for i in *; do mv "$i" "$i.csv"; done
$ ls
venuesaa.csv venuesab.csv venuesac.csv venuesad.csv

# get header of the first file
$ header=$(head -n 1 venuesaa.csv)

# prepend header to every other file
$ ls | grep -v venuesaa | xargs echo -e "$header\n$(cat {})" > {}
```
