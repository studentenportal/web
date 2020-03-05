#!/bin/bash

# Wait for postgres
while ! curl http://$POSTGRES_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d studentenportal -c 'CREATE EXTENSION IF NOT EXISTS citext;'
python3 manage.py migrate front
python3 manage.py migrate
python3 manage.py loaddata ./testdata/database.json
cp -R ./testdata/media/* media/
python3 manage.py runserver 0.0.0.0:8000
