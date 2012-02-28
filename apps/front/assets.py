from django_assets import Bundle, register

scripts = Bundle(
    'js/jquery-1.7.1.js',
    'js/studentenportal.js',
    'js/bootstrap.js',
    filters='jsmin',
    output='js/packed.js')

stylesheets = Bundle(
    'css/style.css',
    'css/bootstrap.css',
    'css/bootstrap-responsive.css',
    'css/responsive-overrides.css',
    filters='cssmin,cssrewrite',
    output='css/packed.css')

register('scripts', scripts)
register('stylesheets', stylesheets)
