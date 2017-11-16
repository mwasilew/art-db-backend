#!/bin/sh

set -ex

get_data() {
  local key="$1"
  sed -e '1,/<<'$key'$/ d; /^'$key'/,$ d' $0
}

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get -qy install python-dev python-pip libffi-dev libssl-dev git wget python-virtualenv openjdk-7-jre-headless
sudo DEBIAN_FRONTEND=noninteractive apt-get install -qy postgresql postgresql-contrib libpq-dev

if [ -d /vagrant ]; then
  cd /vagrant
fi

if [ ! -d ext/art-testing ]; then
  git clone "https://android-review.linaro.org/linaro/art-testing" ext/art-testing
fi
sudo DEBIAN_FRONTEND=noninteractive apt-get install -qy \
  python3-scipy python3-numpy

if [ ! -f .virtualenv/bin/python ]; then
  virtualenv .virtualenv
fi
.virtualenv/bin/pip install --upgrade setuptools
.virtualenv/bin/pip install -r requirements-dev.txt

if [ ! -f crayonbox/settings/private.py ]; then
  get_data DEVELOPMENT_SETTINGS | sed -e "s/\$USER/$USER/g" > crayonbox/settings/private.py
fi

# create database and user
sudo -u postgres createuser --createdb "$USER" || true
sudo -u postgres psql -c "ALTER USER $USER WITH PASSWORD 'test'"
sudo -u postgres psql -d 'template1' -c "CREATE EXTENSION IF NOT EXISTS hstore;"
createdb art-reports || true
.virtualenv/bin/python ./manage.py migrate


########################################################################
# SCRIPT ENDS HERE
########################################################################

: <<DEVELOPMENT_SETTINGS
from . import *

URL = 'http://localhost:8000'

SECRET_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_QUERIES = True
MIDDLEWARE_CLASSES += ( 'qinspect.middleware.QueryInspectMiddleware',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'art-reports',
        'USER': '$USER',
        'HOST': 'localhost',
        'PASSWORD': 'test',
    }
}

LOGGING['loggers']['qinspect'] = { 'handlers': ['console'], 'level': 'DEBUG',
                                   'propagate': True, }

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

EMAIL_REPORTS_TO = [ "$USER@localhost.localdomain", ]

EMAIL_HOST = "localhost"

MEDIA_ROOT = "/var/tmp/art-reports-dev/media"

DEVELOPMENT_SETTINGS

