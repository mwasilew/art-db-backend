from django.conf.urls import include, url
from django.contrib import admin

from userprofile import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),
]
