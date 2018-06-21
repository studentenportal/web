#!/bin/bash
# Expects DOCKER_TAGS to be set.
set -ex

docker build --file=./deploy/production/Dockerfile --tag=studentenportal/studentenportal .

for tag in $DOCKER_TAGS; do
    docker tag studentenportal/studentenportal $tag
done
