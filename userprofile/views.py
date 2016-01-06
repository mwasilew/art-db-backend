from django.template import RequestContext, loader
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    token = Token.objects.get(user=request.user)
    template = loader.get_template('userprofile/index.html')
    context = RequestContext(request, {
        'user': request.user,
        'token': token
    })
    return HttpResponse(template.render(context))
