from . import *


URL = "https://{{ hostname }}"
CELERY_SEND_TASK_ERROR_EMAILS = True
BROKER_URL = 'amqp://guest:guest@localhost:5672/{{hostname}}'

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_LDAP_SERVER_URI = "{{AUTH_LDAP_SERVER_URI}}"
AUTH_LDAP_BIND_DN = '{{AUTH_LDAP_BIND_DN}}'
AUTH_LDAP_BIND_PASSWORD = '{{AUTH_LDAP_BIND_PASSWORD}}'

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
    ),
    "dev-private-review.linaro.org": (
        '{{ dev_private_review_linaro_org_user }}',
        '{{ dev_private_review_linaro_org_password }}'
    ),
    "ci.linaro.org": (
        '{{ ci_linaro_org_user }}',
        '{{ ci_linaro_org_password }}'
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
            'include_html': True,
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '{{logs_base}}/django.log',
            'backupCount': 5,
            'when': 'midnight',
            'encoding': 'utf8',
            'formatter': 'verbose',

        },
        'console': {
            'level': 'DEBUG',
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

DEBUG = False

SERVER_EMAIL = "{{ email }}"
DEFAULT_FROM_EMAIL = "{{ email }}"
ALLOWED_HOSTS = ['{{ hostname }}', '52.90.187.47']

ADMINS = [
    ("Milosz Wasilewski", 'milosz.wasilewski@linaro.org'),
    ("Antonio Terceiro", 'antonio.terceiro@linaro.org')
]

EXTERNAL_DIR = {
    "BASE": os.path.join('{{ext_base}}'),
    "REPOSITORIES": [("art-testing", "https://android-review.linaro.org/linaro/art-testing")]
}

EMAIL_REPORTS_TO = {{email_reports_to}}
