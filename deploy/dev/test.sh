#!/bin/bash

# Wait for postgres
while ! curl http://$DB_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

export PYTHONPATH=$(pwd)

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER  -d template1 -c 'CREATE EXTENSION IF NOT EXISTS citext;'
coverage run --source apps -m pytest "$@" && echo && coverage report
