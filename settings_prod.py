from settings import *

DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SENDFILE_BACKEND = 'sendfile.backends.nginx'
INSTALLED_APPS += ('gunicorn',)
