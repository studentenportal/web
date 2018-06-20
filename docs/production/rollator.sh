#!/bin/bash
set -e

WATCH_FILE=$1
IMAGE=$2
SERVICE=$3

# Remove lock on start
flock -u ${WATCH_FILE} || true

while; do

  # Wait on a change on the watchfile
  notifywait -e create ${WATCH_FILE}

  if [ `flock -n ${WATCH_FILE}` ]; then #TODO: Locking
    while rm touchfile 2>/dev/null; do 
      OLD_IMAGE_HASH=`docker images ${IMAGE} -q`

      docker pull ${IMAGE}
  
      if [ "`docker images ${IMAGE} -q`" == "${OLD_IMAGE_HASH}" ]; then
        systemctl restart ${SERVICE}
      fi
    done
    flock -u ${WATCH_FILE}
  fi
done
