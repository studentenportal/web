#!/bin/bash

export DB_HOST="postgres" \
	DB_USER="${POSTGRES_USER}" \
	DB_NAME="${POSTGRES_DB_NAME}" \
	DB_PASSWORD="${POSTGRES_PASSWORD}" \
	DJANGO_SETTINGS_MODULE="config.settings" \
	DJANGO_DEBUG="false" \
	DJANGO_STATIC_ROOT="/srv/www/studentenportal/static" \
	DJANGO_MEDIA_ROOT="/srv/www/studentenportal/media" \
	PORT="8000"

# Wait for postgres
while ! curl http://$DB_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS citext;'

python3 manage.py migrate front
python3 manage.py migrate
python3 manage.py collectstatic

# FIXME Python 3?
gunicorn config.wsgi:application -n studentenportal -b 0.0.0.0:8000 -w 4 --log-level warning
