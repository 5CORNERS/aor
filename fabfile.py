#!/usr/bin/env python
from fabric.api import *
import urllib
import urllib2
import os
try:
    from aor.settings import CLOUDFLARE_TOKEN, CLOUDFLARE_EMAIL
except ImportError:
    CLOUDFLARE_TOKEN = None
    CLOUDFLARE_EMAIL = None

PROJECT_NAME = 'archlinux'
HOME = '/home/zeus'
PROJECT_SOURCE = 'git@github.com:hovel/aor.git'
PROJECT_BASEDIR = '%s/%s' % (HOME, PROJECT_NAME)
PYTHON_PATH = '%s/.virtualenvs/%s/bin/python' % (HOME, PROJECT_NAME)
PIP_PATH = '%s/.virtualenvs/%s/bin/pip' % (HOME, PROJECT_NAME)
env.use_ssh_config = True
env.sudo_user = 'zeus'

all_hosts = []
i = 1
while True:
    host = os.environ.get('HOST%s' % i)
    if host:
        all_hosts.append(host)
    else:
        break
    i += 1
env.hosts = all_hosts


def uninstall():
    with cd(HOME):
        sudo('rm -rf %s' % PROJECT_BASEDIR)


def install():
    with cd(HOME):
        sudo('mkvirtualenv %s' % PROJECT_NAME)
        sudo('git clone %s %s' % (PROJECT_SOURCE, PROJECT_NAME))
        sudo('touch %s/logs/%s.log' % (HOME, PROJECT_NAME))
        sudo('touch %s/logs/%s-error.log' % (HOME, PROJECT_NAME))
    put_settings()
    copy_nginx_config()
    update()
    start()


def update():
    db_backup()
    with cd(PROJECT_BASEDIR):
        sudo('git pull')
        sudo('%s install -r build/pipreq.txt -U' % PIP_PATH)
        sudo('%s manage.py syncdb' % PYTHON_PATH)
        sudo('%s manage.py migrate' % PYTHON_PATH)
        sudo('%s manage.py syncdb --all' % PYTHON_PATH)
        sudo('%s manage.py collectstatic --noinput' % PYTHON_PATH)
        sudo('./gunicorn.sh reload')
    purge_clouflare_static()


def start():
    with cd(PROJECT_BASEDIR):
        sudo('./gunicorn.sh start')


def stop():
    with cd(PROJECT_BASEDIR):
        sudo('./gunicorn.sh stop')


def restart():
    with cd(PROJECT_BASEDIR):
        sudo('./gunicorn.sh restart')


def reload():
    with cd(PROJECT_BASEDIR):
        sudo('./gunicorn.sh reload')


def db_backup():
    with cd(PROJECT_BASEDIR):
        sudo('./db_backup.sh')


def put_settings():
    put('conf/local.py', '%s/aor/settings_local.py' % PROJECT_BASEDIR, use_sudo=True, temp_dir='/home/zeus/tmp')
    with settings(sudo_user='root'):
        sudo('chown zeus:zeus %s/aor/settings_local.py' % PROJECT_BASEDIR)


def put_backup_script():
    put('conf/db_backup.sh', '%s/db_backup.sh' % PROJECT_BASEDIR, use_sudo=True, temp_dir='/home/zeus/tmp')
    with settings(sudo_user='root'):
        sudo('chown zeus:zeus %s/db_backup.sh' % PROJECT_BASEDIR)
        sudo('chmod +x %s/db_backup.sh' % PROJECT_BASEDIR)


def copy_nginx_config():
    with settings(sudo_user='root'), cd(PROJECT_BASEDIR):
        sudo('cp conf/archlinux.conf /etc/nginx/conf.d/archlinux.conf')
        sudo('/etc/init.d/nginx restart')


def purge_clouflare_static():
    token = os.environ.get('CLOUDFLARE_TOKEN', CLOUDFLARE_TOKEN)
    email = os.environ.get('CLOUDFLARE_EMAIL', CLOUDFLARE_EMAIL)
    if not token or not email:
        print 'purge static files failed'
        return

    response = urllib2.urlopen('https://www.cloudflare.com/api_json.html',
                               data=urllib.urlencode({
                                   'a': 'fpurge_ts',
                                   'tkn': token,
                                   'email': email,
                                   'z': 'archlinux.org.ru',
                                   'v': '1'
                               }))
    print response.read()