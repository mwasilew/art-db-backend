from django.conf.urls import include, url
from django.conf.urls.static import static

from django.conf import settings
from django.contrib import admin

from userprofile import views
# from frontend import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

