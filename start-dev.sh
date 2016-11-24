#!/bin/bash

# Wait for postgre
while ! curl http://$DB_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER  -d studentenportal -c 'CREATE EXTENSION IF NOT EXISTS citext;'
python manage.py syncdb
python manage.py migrate --all
python manage.py runserver 0.0.0.0:8000
