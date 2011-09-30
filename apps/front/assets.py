from django_assets import Bundle, register

scripts = Bundle(
    filters='jsmin',
    output='js/packed.js')

stylesheets = Bundle(
    #'css/reset.css',
    'css/bootstrap.css',
    'css/style.css',
    filters='cssmin,cssrewrite',
    output='css/packed.css')

register('scripts', scripts)
register('stylesheets', stylesheets)
