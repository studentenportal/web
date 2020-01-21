# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
import sys
import datetime

from unipath import Path

from django.core.exceptions import ImproperlyConfigured


env = os.environ.get
true_values = ['1', 'true', 'y', 'yes', 1, True]


def require_env(name):
    value = env(name)
    if not value:
        raise ImproperlyConfigured('Missing {} env variable'.format(name))
    return value


PROJECT_ROOT = Path(__file__).ancestor(2)

ADMINS = (
    ('Studentenportal Team', 'team@studentenportal.ch'),
)

MANAGERS = ADMINS

# Debug config
DEBUG = env('DJANGO_DEBUG', 'True').lower() in true_values
DEBUG_TOOLBAR = env('DJANGO_DEBUG_TOOLBAR', 'False').lower() in true_values
THUMBNAIL_DEBUG = DEBUG
COMPRESS_ENABLED = env('DJANGO_COMPRESS', str(not DEBUG)).lower() in true_values

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-ch'

SITE_ID = 1

# Security
CSRF_COOKIE_HTTPONLY = True
if not DEBUG:
    ALLOWED_HOSTS = ['studentenportal.ch', 'www.studentenportal.ch']
    CSRF_COOKIE_SECURE = True

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME', 'studentenportal'),
        'USER': env('DB_USER', 'studentenportal'),
        'PASSWORD': env('DB_PASSWORD', 'studentenportal'),
        'HOST': env('DB_HOST', 'localhost'),
        'PORT': env('DB_PORT', ''),
    }
}

SECRET_KEY = env('SECRET_KEY', 'DEBUG_SECRET_KEY')
if SECRET_KEY == 'DEBUG_SECRET_KEY' and DEBUG is False:
    raise ImproperlyConfigured('Missing SECRET_KEY env variable')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT', PROJECT_ROOT.child('media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = env('DJANGO_STATIC_ROOT', PROJECT_ROOT.child('static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# DEPRECATED!
# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
#ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_OFFLINE = not DEBUG

COMPRESS_PRECOMPILERS = (
    ('text/scss',
     '{} -mscss '.format(sys.executable) +
     ' --load-path "apps/front/static/sass/compass/compass/stylesheets"'    # Legacy :(
     ' --load-path "apps/front/static/sass/compass/blueprint/stylesheets"'  # sory...
     ' -C -o {outfile} {infile}'),
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'apps.front.context_processors.global_stats',
            'apps.front.context_processors.debug',
        ]
    }
}]

MIDDLEWARE = []
if DEBUG_TOOLBAR:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MAX_UPLOAD_SIZE = 1024 * 1024 * 20 # 20MB

AUTH_USER_MODEL = 'front.User'

INSTALLED_APPS = (
    # Builtin apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'compressor',
    'apps.tabs',
    'mathfilters',
    'easy_thumbnails',
    'rest_framework',

    # Own apps
    'apps.front',
    'apps.documents',
    'apps.events',
    'apps.lecturers',
    'apps.tweets',
    'apps.api',
    'apps.user_stats',

    # Overridable 3rd party apps
    'messagegroups',
    'registration',

    # Django admin (overrideable templates)
    'django.contrib.admin',
    'django.contrib.admindocs',
)
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django.request': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}
if not DEBUG:
    LOGGING['loggers']['django.request'] = {
        'level': 'WARNING',
        'handlers': ['mail_admins', 'console'],
        'propagate': False,
    }

# Email
DEFAULT_FROM_EMAIL = 'Studentenportal <noreply@studentenportal.ch>'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Sendfile
if DEBUG:
    SENDFILE_BACKEND = 'sendfile.backends.development'
else:
    SENDFILE_BACKEND = 'sendfile.backends.nginx'
    SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'documents')
    SENDFILE_URL = MEDIA_URL + 'documents/'

# Auth
LOGIN_REDIRECT_URL = '/'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# API
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}
OAUTH_EXPIRE_DELTA = datetime.timedelta(days=90)
OAUTH_ENFORCE_SECURE = not DEBUG

# Registration
REGISTRATION_OPEN = True
REGISTRATION_FORM = 'apps.front.forms.HsrRegistrationForm'
REGISTRATION_EMAIL_HTML = False
ACCOUNT_ACTIVATION_DAYS = 7

# Analytics
GOOGLE_ANALYTICS_CODE = env('GOOGLE_ANALYTICS_CODE', None)


# DEBUG TOOLBAR
def show_debug_toolbar(request):
    return DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'config.settings.show_debug_toolbar',
}
