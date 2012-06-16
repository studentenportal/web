from fabric.api import settings, abort, local, cd, sudo, env
from fabric.contrib.console import confirm

env.hosts = ['dbargen@studentenportal.ch']

def test():
    """Run django tests."""
    with settings(warn_only=True):
        local('./manage.py collectstatic --noinput --link')
        result = local('./manage.py test front --failfast')
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def push():
    """Do everything needed before deployment."""
    test()
    local('git push')

def deploy_untested():
    """Prepare & run deployment without testing."""
    code_dir = '/var/www/studentenportal'
    with cd(code_dir):
        sudo('git pull', user='django')
        sudo('VIRTUAL/bin/pip install -r requirements.txt', user='django')
        sudo('VIRTUAL/bin/pip install -r requirements_prod.txt', user='django')
        sudo('VIRTUAL/bin/python manage.py collectstatic --noinput --clear --settings=settings_prod', user='django')
        sudo('/etc/init.d/supervisor restart')

def deploy():
    """Prepare, test & run deployment."""
    test()
    deploy_untested()
