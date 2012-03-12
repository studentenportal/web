from settings import *

DEBUG = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'documents')
SENDFILE_URL = MEDIA_URL + 'documents/'
INSTALLED_APPS += ('gunicorn',)
