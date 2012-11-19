# coding=utf-8
from settings_base import *
import os

# Helper function
env = os.environ.get

DEBUG = False
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = not DEBUG

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

INSTALLED_APPS += ('gunicorn',)
SENTRY_DSN = env('SENTRY_DSN')
