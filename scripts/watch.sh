#!/bin/bash

browser-sync start --config bs-config.js --port 3000 &
find . \
  -name '*.html' \
  -o -name '*.css' \
  -o -name '*.py' | grep -v output | grep -v venv | entr sh -c 'source .env && python build.py && browser-sync reload'
