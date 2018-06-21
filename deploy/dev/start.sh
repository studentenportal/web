#!/bin/bash

# Wait for postgres
while ! curl http://$DB_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d studentenportal -c 'CREATE EXTENSION IF NOT EXISTS citext;'
python manage.py migrate front
python manage.py migrate
python manage.py loaddata ./testdata/database.json
cp -R ./testdata/media/* media/
python manage.py runserver 0.0.0.0:8000
