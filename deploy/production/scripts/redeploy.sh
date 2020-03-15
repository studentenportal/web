#!/bin/bash
export UID=$(id -u)
export GID=$(id -g)
docker-compose -f docker-compose-production.yml up --no-deps --build -d studentenportal
