# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
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
    ('Danilo', 'mail@dbrgn.ch'),
)

MANAGERS = ADMINS

# Debug config
DEBUG = env('DJANGO_DEBUG', 'True').lower() in true_values
DEBUG_TOOLBAR = env('DJANGO_DEBUG_TOOLBAR', 'False').lower() in true_values
TEMPLATE_DEBUG = DEBUG
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

if not DEBUG:
    ALLOWED_HOSTS = ['studentenportal.ch', 'www.studentenportal.ch']

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
        'HOST': env('DB_HOST', ''),
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
    'dajaxice.finders.DajaxiceFinder',
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "apps.front.context_processors.global_stats"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'config.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MAX_UPLOAD_SIZE = 10485760  # 10MB

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
    'messagegroups',
    'apps.tabs',
    'registration',
    'django_extensions',
    'south',
    'dajaxice',
    'mathfilters',
    'easy_thumbnails',
    'rest_framework',
    'provider',
    'provider.oauth2',

    # Own apps
    'apps.front',
    'apps.api',
    'apps.events',
    'apps.user_stats',
    'apps.lecturers',

    # Django admin (overrideable templates)
    'django.contrib.admin',
    'django.contrib.admindocs',
)
if not DEBUG:
    INSTALLED_APPS += ('raven.contrib.django')
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
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
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
        'dajaxice': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['mail_admins'],
            'propagate': False,
        },
    }
}
if not DEBUG:
    LOGGING['root'] = {
        'level': 'WARNING',
        'handlers': ['sentry'],
    }
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }
    LOGGING['loggers']['django.request'] = {
        'level': 'WARNING',
        'handlers': ['sentry'],
        'propagate': False,
    }
    LOGGING['loggers']['dajaxice'] = {
        'handlers': ['sentry'],
        'level': 'WARNING',
        'propagate': False,
    }
    LOGGING['loggers']['raven'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': False,
    }


# Sentry
if not DEBUG:
    SENTRY_DSN = require_env('SENTRY_DSN')

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
AUTHENTICATION_BACKENDS = ('config.backends.CaseInsensitiveModelBackend',)

# API
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'page_size',
}
OAUTH_EXPIRE_DELTA = datetime.timedelta(days=90)
OAUTH_ENFORCE_SECURE = not DEBUG

# Registration
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

# South
SOUTH_TESTS_MIGRATE = False

# Testing
TEST_RUNNER = 'discover_runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = PROJECT_ROOT
TEST_DISCOVER_ROOT = PROJECT_ROOT
TEST_DISCOVER_PATTERN = 'test*.py'


# DEBUG TOOLBAR
def show_debug_toolbar(request):
    return DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': 'config.settigns.show_debug_toolbar',
}
