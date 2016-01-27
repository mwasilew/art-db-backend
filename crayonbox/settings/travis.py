from . import *

SECRET_KEY = '0Z$wOPv'

AUTH_CROWD_ALWAYS_UPDATE_USER = False
AUTH_CROWD_ALWAYS_UPDATE_GROUPS = False
AUTH_CROWD_APPLICATION_USER = "test"
AUTH_CROWD_APPLICATION_PASSWORD = "test"
AUTH_CROWD_SERVER_REST_URI = "test"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'art-reports',
        'USER': 'postgres',
        'PASSWORD': 'art-reports',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


EXTERNAL_DIR = {
    "BASE": os.path.join(BASE_DIR, 'ext'),
    "REPOSITORIES": [("art-testing", "https://android-review.linaro.org/linaro/art-testing")]
}
