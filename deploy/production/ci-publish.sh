#!/bin/bash
# Expects DOCKER_PASSWORD, DOCKER_USERNAME and DOCKER_TAGS to be set.
set -euxo pipefail

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

for tag in $DOCKER_TAGS; do
    docker push "$tag"
done
