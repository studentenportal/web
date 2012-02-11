from settings import *

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
INSTALLED_APPS += ('gunicorn')
