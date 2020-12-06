#!/bin/bash


export POSTGRES_HOST="postgres" \
	DJANGO_SETTINGS_MODULE="config.settings" \
	DJANGO_DEBUG="false" \
	DJANGO_STATIC_ROOT="/srv/www/studentenportal/static" \
	DJANGO_MEDIA_ROOT="/srv/www/studentenportal/media" \
	PORT="8000"

# Wait for postgres
while ! curl http://$POSTGRES_HOST:5432/ 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

python3 manage.py migrate front
python3 manage.py migrate
python3 manage.py collectstatic --clear --no-input -v 0
python3 manage.py compress

gunicorn config.wsgi:application -n studentenportal -b 0.0.0.0:8000 -w 4 --log-level warning
