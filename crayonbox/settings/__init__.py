import os
import djcelery

from datetime import timedelta

djcelery.setup_loader()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

SECRET_KEY = 'very-secret-password'

DEBUG = True

ALLOWED_HOSTS = []
APPEND_SLASH = False

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login"
LOGOUT_URL = "/logout"

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


INSTALLED_APPS = (
    'longusername',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'rest_framework',
    'rest_framework.authtoken',
    'djcelery',

    # local apps
    'benchmarks',
    'jobs',
    'api',
    'userprofile',
    'frontend'
)


REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'crayonbox.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR + '/templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    }
}]

WSGI_APPLICATION = 'crayonbox.wsgi.application'

BENCHMARK_MANIFEST_PROJECT_LIST = [
    'linaro-art/platform/bionic',
    'linaro-art/platform/build',
    'linaro-art/platform/external/vixl',
    'linaro-art/platform/art'
]

LAVA_CREDENTIALS = {
    'host.url.netloc': ('username', 'password'),
}


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERYBEAT_SCHEDULE_FILENAME = "/tmp/celery-beat"

CELERYBEAT_SCHEDULE = {
   'check_incomplete_testjob': {
       'task': 'jobs.tasks.update_incopleted_testjobs',
       'schedule': timedelta(minutes=1),
   },
}
