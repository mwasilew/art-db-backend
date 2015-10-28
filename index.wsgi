import os
import sys

sys.path.append('/srv/art-reports.linaro.org/project')
sys.path.append('/srv/art-reports.linaro.org/project/crayonbox/')
sys.path.append('/srv/art-reports.linaro.org/.virtualenv/lib/python2.7/site-packages/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'crayonbox.settings'

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crayonbox.settings")
application = get_wsgi_application()
