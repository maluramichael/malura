#!/bin/bash

rev=HEAD
for f in $(git ls-tree -r -t --full-name --name-only "$rev") ; do
  file_name=$(git log --pretty=format:%cI -1 "$rev" -- "$f")
  touch -d "$file_name" "$f";
done