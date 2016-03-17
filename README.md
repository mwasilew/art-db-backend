# art-reports

## setup (ubuntu)

1) required system packages

```
sudo apt-get install python-dev python-pip libffi-dev libssl-dev git
```

1) postgresql

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list.d/postgresql.list'
sudo apt-get update
sudo apt-get install postgresql-9.5 postgresql-contrib-9.5 libpq-dev
```

1) required python packages

```
sudo pip install -U pip virtualenv
```

1) project packages

```
virtualenv .virtualenv/
source .virtualenv/bin/activate
pip install -r requirements.txt
```


## configure

1) create `crayonbox/settings/private.py`, append with the content, modify to the needs

```
from . import *

SECRET_KEY = "FAKE-TOKEN"

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

3) setup external repos (ext)


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

### staging

```bash
ansible-playbook ansible/site.yml -i ansible/hosts -l staging-art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```

### production

```bash
ansible-playbook ansible/site.yml -i ansible/hosts -l art-reports.linaro.org -u {{ USER }} --ask-become-pass [[-e branch=oter-branch] [-e repo=other-repo]]
```
