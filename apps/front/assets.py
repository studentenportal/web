from django_assets import Bundle, register

scripts = Bundle(
    'js/studentenportal.js',
    'js/bootstrap.js',
    'js/jquery.min.js',
    filters='jsmin',
    output='js/packed.js')

stylesheets = Bundle(
    'css/bootstrap.css',
    'css/style.css',
    filters='cssmin,cssrewrite',
    output='css/packed.css')

register('scripts', scripts)
register('stylesheets', stylesheets)
