#!/bin/bash

RELEASE=prod
OUTPUT_DIR=_output
HOST=$1
DESTINATION="/var/www/malura/${RELEASE}/"

if ! rsync -ra --progress --delete "${OUTPUT_DIR}/" "${HOST}":"${DESTINATION}"; then exit 1; fi
if ! rsync -ra --progress nginx.conf "${HOST}:/etc/nginx/sites/malura.de.conf"; then exit 1; fi
if ! rsync -ra --progress redirects.map "${HOST}":"${DESTINATION}"; then exit 1; fi
if ! rsync -ra --progress generatestats "${HOST}:/etc/cron.hourly/"; then exit 1; fi

ssh $HOST <<EOF
    cd ${DESTINATION}
    chown -R root:root /etc/cron.hourly/generatestats
    chmod -R 755 /etc/cron.hourly/generatestats

    chown -R www-data:www-data ${DESTINATION}
    chmod -R 755 ${DESTINATION}

    systemctl reload nginx
    systemctl restart cron
EOF
