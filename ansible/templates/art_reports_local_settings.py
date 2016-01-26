import sys

from . import *


DEFAULT_FROM_EMAIL = "{{ email }}"
CELERY_DEFAULT_QUEUE = "{{ hostname }}"

AUTH_CROWD_ALWAYS_UPDATE_USER = False
AUTH_CROWD_ALWAYS_UPDATE_GROUPS = False
AUTH_CROWD_APPLICATION_USER = '{{crowd_user}}'
AUTH_CROWD_APPLICATION_PASSWORD = '{{crowd_pass}}'
AUTH_CROWD_SERVER_REST_URI = '{{crowd_rest_uri}}'

AUTHENTICATION_BACKENDS = (
    'crowdrest.backend.CrowdRestBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CREDENTIALS = {
    'validation.linaro.org': ('{{lava_user}}', '{{lava_key}}')
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{db_name}}',
        'USER': '{{db_user}}',
        'PASSWORD': '{{db_password}}',
        'HOST': '{{db_host}}',
        'PORT': '{{db_port}}',
    }
}

SECRET_KEY = '{{secret_key}}'

STATIC_ROOT = '/var/www/{{hostname}}/static/'
MEDIA_ROOT = '{{media_base}}'
LOG_LEVEL = 'DEBUG'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level':'DEBUG',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': '{{logs_base}}/django.log',
            'backupCount': 5,
            'when': 'midnight',
            'encoding': 'utf8',
            'formatter': 'verbose',

        },
        'console': {
            'level':'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'scripts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

DEBUG=False

SERVER_EMAIL = "{{ email }}"
DEFAULT_FROM_EMAIL = "{{ email }}"

ALLOWED_HOSTS = ['{{ hostname }}']

ADMINS = [("Sebastian Pawlus", 'sebastian.pawlus@linaro.org')]
