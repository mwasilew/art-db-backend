import os
import sys
import site

# Add the app's directory to the PYTHONPATH
sys.path.append('/srv/art-reports.linaro.org/project')
sys.path.append('/srv/art-reports.linaro.org/project/crayonbox/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'crayonbox.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
