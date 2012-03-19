from settings_base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ASSETS_DEBUG = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'Studentenportal <noreply@studentenportal.ch>'

SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'documents')
SENDFILE_URL = MEDIA_URL + 'documents/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'studentenportal',       # Or path to database file if using sqlite3.
        'USER': 'django',                # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS += ('gunicorn',)
