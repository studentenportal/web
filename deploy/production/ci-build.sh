#!/bin/bash
# Expects DOCKER_TAGS and DOCKER_TAGS_NGINX to be set.
set -euxo pipefail

docker build --file=./deploy/production/Dockerfile --tag=studentenportal/web .
for tag in $DOCKER_TAGS; do
    docker tag studentenportal/web "$tag"
done

docker build --file=./deploy/production/nginx/Dockerfile --tag=studentenportal/nginx .
for tag in $DOCKER_TAGS_NGINX; do
    docker tag studentenportal/nginx "$tag"
done
