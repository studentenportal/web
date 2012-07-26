# coding=utf-8
from settings_base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ASSETS_DEBUG = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SENDFILE_BACKEND = 'sendfile.backends.development'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'south',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'studentenportal',
        'USER': 'studentenportal',
        'PASSWORD': 'studentenportal',
        'HOST': '',  # Set to empty string for localhost.
        'PORT': '',  # Set to empty string for default.
    }
}

### DEBUG TOOLBAR ###

def local_network_debug(request):
    """Returns True if IP is internal and DEBUG = True."""
    return DEBUG and request.META['REMOTE_ADDR'].startswith(('127.0.0', '192.168.1', '192.168.2'))

DEBUG_TOOLBAR_PANELS = ( 
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)
DEBUG_TOOLBAR_CONFIG = { 
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': local_network_debug,
}
