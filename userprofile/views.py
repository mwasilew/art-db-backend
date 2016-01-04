from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import views as static
from rest_framework.authtoken.models import Token


@login_required
def index(request):
    return static.serve(request, 'index.html', insecure=True)

