#!/bin/bash
# Expects DOCKER_PASSWORD, DOCKER_USERNAME, DOCKER_TAGS and DOCKER_TAGS_NGINX to be set.
set -euxo pipefail

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for tag in $DOCKER_TAGS $DOCKER_TAGS_NGINX; do
    docker push "$tag"
done
