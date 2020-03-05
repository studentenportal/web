#!/bin/bash

# Wait for postgres
while ! curl http://$POSTGRES_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

export PYTHONPATH=$(pwd)

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER  -d template1 -c 'CREATE EXTENSION IF NOT EXISTS citext;'
coverage run --source apps -m pytest "$@" && echo && coverage report
