from fabric.api import settings, abort, local, cd, sudo, env, prefix
from fabric.contrib.console import confirm

env.hosts = ['dbargen@studentenportal.ch']

def test():
    """Run django tests."""
    with settings(warn_only=True):
        local('./manage.py collectstatic --noinput --link')
        result = local('./test.sh --failfast')
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
        with prefix('source /var/www/studentenportal/env'):
            sudo('git pull', user='django')
            sudo('VIRTUAL/bin/pip install -r requirements/production.txt', user='django')
            sudo('VIRTUAL/bin/python manage.py syncdb --noinput --settings=settings_prod', user='django')
            sudo('VIRTUAL/bin/python manage.py migrate --noinput --settings=settings_prod', user='django')
            sudo('VIRTUAL/bin/python manage.py collectstatic --noinput --clear --settings=settings_prod', user='django')
            sudo('VIRTUAL/bin/python manage.py compress --settings=settings_prod', user='django')
            sudo('/etc/init.d/supervisor restart')

def deploy():
    """Prepare, test & run deployment."""
    test()
    deploy_untested()

def publish():
    """Test, push & deploy."""
    push()
    deploy_untested()
