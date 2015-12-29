import sys

AUTH_CROWD_ALWAYS_UPDATE_USER = False
AUTH_CROWD_ALWAYS_UPDATE_GROUPS = False
AUTH_CROWD_APPLICATION_USER = '{{crowd_user}}'
AUTH_CROWD_APPLICATION_PASSWORD = '{{crowd_pass}}'
AUTH_CROWD_SERVER_REST_URI = '{{crowd_rest_uri}}'

AUTHENTICATION_BACKENDS = (
    'crowdrest.backend.CrowdRestBackend',
    'django.contrib.auth.backends.ModelBackend',
)

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

LOG_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'simple': {
            'format': u'[%(asctime)s] %(levelname)-8s %(message)s',
        }
    },
    'handlers': {
        'console':{
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter':'simple'
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/{{hostname}}/art-reports.log',
            'backupCount': 5,
            'when': 'midnight',
            'formatter': 'simple',
            'encoding': 'utf8',
            'delay': True,
        }
    },
    'loggers': {
        'testplanner': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
            'filters': ['require_debug_true'],
            'propagate': False,
        },
        'testrunner': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
            'filters': ['require_debug_true'],
            'propagate': False,
        },
    }
}


DEBUG=True
