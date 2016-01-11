import os
import sys
import site

activate_env=os.path.expanduser("/srv/{{hostname}}/.virtualenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

sys.path.append('/srv/{{hostname}}/project')
sys.path.append('/srv/{{hostname}}/project/crayonbox/')

import djcelery
from django.core.wsgi import get_wsgi_application

djcelery.setup_loader()

os.environ['DJANGO_SETTINGS_MODULE'] = "crayonbox.settings.private"
application = get_wsgi_application()
