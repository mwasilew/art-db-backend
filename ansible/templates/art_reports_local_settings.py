import sys

from . import *

BROKER_URL = '{{ broker_url }}'

HOST = "{{ hostname }}"
CELERY_DEFAULT_QUEUE = "{{ hostname }}"
CELERY_SEND_TASK_ERROR_EMAILS = True

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
    'validation.linaro.org': (
        '{{ validation_linaro_org_user }}',
        '{{ validation_linaro_org_password }}'
    ),
    'review.linaro.org': (
        '{{ review_linaro_org_user }}',
        '{{ review_linaro_org_password }}'
    ),
    'android-build.linaro.org': (
        '{{ android_build_linaro_org_user }}',
        '{{ android_build_linaro_org_password }}'
    ),
    'android-review.linaro.org': (
        '{{ android_review_linaro_org_user }}',
        '{{ android_review_linaro_org_password }}'
    )
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
        'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
        },
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
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'tasks': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'celery': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

DEBUG=False

SERVER_EMAIL = "{{ email }}"
DEFAULT_FROM_EMAIL = "{{ email }}"
ALLOWED_HOSTS = ['{{ hostname }}']

ADMINS = [
    ("Milosz Wasilewski", 'milosz.wasilewski@linaro.org'),
    ("Sebastian Pawlus", 'sebastian.pawlus@linaro.org')
]

EXTERNAL_DIR = {
    "BASE": os.path.join('{{ext_base}}'),
    "REPOSITORIES": [("art-testing", "https://android-review.linaro.org/linaro/art-testing")]
}

EMAIL_REPORTS_TO = [
    "sebastian.pawlus@linaro.org",
    "milosz.wasilewski@linaro.org"
]
