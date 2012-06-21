from django_assets import Bundle, register


scripts = Bundle(
    'js/jquery-1.7.1.js',
    'js/bootstrap.js',
    'js/jquery.raty.min.js',
    'js/studentenportal.js',
    'js/raty.js',
    output='js/packed.js')


flattr_js = Bundle(
    'js/flattr_loader.js',
    filters='jsmin',
    output='js/flattr_loader.min.js')


stylesheets = Bundle(
    'css/style.css',
    'css/bootstrap.css',
    'css/bootstrap-responsive.css',
    #filters='cssmin,cssrewrite',
    output='css/packed.css')


register('scripts', scripts)
register('stylesheets', stylesheets)
register('flattr_js', flattr_js)
