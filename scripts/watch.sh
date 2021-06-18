#!/bin/bash

browser-sync start --config bs-config.js &
find . -name '*.html' -o -name '*.css' | grep -v output | entr sh -c 'source .env && python build.py && browser-sync reload'
