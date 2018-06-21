#!/bin/bash
# Expects DOCKER_TAGS to be set.
set -ex

TAGS_CMD=`for tag in $DOCKER_TAGS; do echo -n "--tag='$tag' "; done`
docker build --file=./deploy/production/Dockerfile $TAGS_CMD
