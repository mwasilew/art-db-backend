import os
import sys
import site

site.addsitedir('/srv/{{hostname}}/local/lib/python2.7/site-packages')

import djcelery
from django.core.wsgi import get_wsgi_application

djcelery.setup_loader()

sys.path.append('/srv/{{hostname}}/project')
sys.path.append('/srv/{{hostname}}/project/crayonbox/')

activate_env=os.path.expanduser("/srv/{{hostname}}/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

os.environ['DJANGO_SETTINGS_MODULE'] = "crayonbox.settings"
application = get_wsgi_application()
