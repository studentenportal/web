#!/bin/bash

export	DB_HOST="postgres" \
	DB_USER="${POSTGRES_USER}" \
	DB_NAME="${POSTGRES_DB_NAME}" \
	DB_PASSWORD="${POSTGRES_PASSWORD}" \
	DJANGO_SETTINGS_MODULE="config.settings" \
	DJANGO_DEBUG="false" \
	DJANGO_STATIC_ROOT="/srv/www/static" \
	DJANGO_MEDIA_ROOT="/srv/www/media" \
	PORT="8000"

# Wait for postgres
while ! curl http://$DB_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

python manage.py syncdb
python manage.py migrate --all

gunicorn config.wsgi:application -n studentenportal -b 0.0.0.0:8000 -w 4 --log-level warning
