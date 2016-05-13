# art-reports

## quick start with vagrant

```
vagrant up
vagrant ssh
```

Inside the VM, you need to start the development server manually:

```
cd /vagrant
source .virtualenv/bin/activate
./manage.py runserver 0.0.0.0:0000
```

Then the web UI will be available from your host machine at
http://localhost:8000/

## setup (ubuntu)

1) required system packages

```
sudo apt-get install python-dev python-pip libffi-dev libssl-dev git wget
```

2) postgresql

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list.d/postgresql.list'
sudo apt-get update
sudo apt-get install postgresql-9.5 postgresql-contrib-9.5 libpq-dev
```

3) required python packages

```
sudo pip install -U pip virtualenv
```

4) project packages

```
virtualenv .virtualenv/
source .virtualenv/bin/activate
pip install -r requirements-dev.txt
```

5) auxiliar sub-project

```
mkdir -p ext
git clone https://android-review.linaro.org/linaro/art-testing ext/art-testing
```

## configure

1) create `crayonbox/settings/private.py`, append with the content, modify to the needs

```
from . import *

SECRET_KEY = "FAKE-TOKEN"

DEBUG = False

QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_QUERIES = True
MIDDLEWARE_CLASSES += (
	'qinspect.middleware.QueryInspectMiddleware',
)

DATABASES = {
    'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'art-reports',
		'USER': 'art-reports'
    }
}

LOGGING['loggers']['qinspect'] = {
	'handlers': ['console'],
    'level': 'DEBUG',
	'propagate': True,
}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

EMAIL_REPORTS_TO = [
    "account@linaro.org",
]

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "account@linaro.org"
EMAIL_HOST_PASSWORD = "password"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

2) configure database

In `/etc/postgresql/9.5/main/pg_hba.conf` change
change line `local all all md5` to `local all all trust`

```
sudo service postgresql restart
```

```
sudo -u postgres bash
createuser art-reports -d
createdb -U art-reports art-reports
exit
```

```
python manage.py migrate
```

### development server
```
source .virtualenv/bin/activate
honcho start
```


### tests
```
source .virtualenv/bin/activate
python manage.py test
```


## deploy

* default branch for deployment `master`
* default repository for deployment `https://git.linaro.org/people/milosz.wasilewski/art-db-backend.git`

Those can be changed with `-e` option

Controlling the celery daemons:

```
sudo -u www-data supervisorctl -c /srv/supervisor/config.conf COMMAND [ARGS]
``

### deploying

Clone secrets repository from ssh://git@dev-private-git.linaro.org/qa/art-reports-secrets.git
The destination directory should be ansible/secrets

basic steps:

```
cd ansible/
git clone ssh://git@dev-private-git.linaro.org/qa/art-reports-secrets.git secrets
./ansible-playbook --sudo-ask-pass -l production # or -l staging etc
```

### staging

```bash
ansible-playbook --vault-password-file='vault-passwd' ansible/site.yml -i ansible/hosts -l staging-art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```

### production

```bash
ansible-playbook --vault-password-file='vault-passwd' ansible/site.yml -i ansible/hosts -l art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```
