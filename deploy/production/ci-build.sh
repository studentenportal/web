#!/bin/bash
# Expects DOCKER_TAGS to be set.
set -euxo pipefail

docker build --file=./deploy/production/Dockerfile --tag=studentenportal/web .
for tag in $DOCKER_TAGS; do
    docker tag studentenportal/web "$tag"
done
