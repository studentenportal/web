from settings import *

DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
INSTALLED_APPS += ('gunicorn')
