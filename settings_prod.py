# -*- coding: utf-8 -*-

import os

from django.core.exceptions import ImproperlyConfigured

from settings_base import *


env = os.environ.get


DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = not DEBUG

ALLOWED_HOSTS = ['studentenportal.ch', 'www.studentenportal.ch']

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'Studentenportal <noreply@studentenportal.ch>'

SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'documents')
SENDFILE_URL = MEDIA_URL + 'documents/'

COMPRESS_OFFLINE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME', 'studentenportal'),
        'USER': env('DB_USER', 'studentenportal'),
        'PASSWORD': env('DB_PASSWORD', ''),
        'HOST': env('DB_HOST', ''),  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': env('DB_PORT', ''),  # Set to empty string for default. Not used with sqlite3.
    }
}

LOGGING['root'] = {
    'level': 'WARNING',
    'handlers': ['sentry'],
}
LOGGING['handlers']['sentry'] = {
    'level': 'ERROR',
    'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
}
LOGGING['loggers']['sentry.errors'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}
LOGGING['loggers']['raven'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}
LOGGING['loggers']['dajaxice'] = {
    'handlers': ['sentry'],
    'level': 'WARNING',
    'propagate': False,
}

SECRET_KEY = env('SECRET_KEY')
if SECRET_KEY is None:
    raise ImproperlyConfigured('Missing SECRET_KEY env variable')

INSTALLED_APPS += ('gunicorn', 'raven.contrib.django')
SENTRY_DSN = env('SENTRY_DSN')
