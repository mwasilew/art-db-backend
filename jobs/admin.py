from django.contrib import admin
from django.contrib import admin

from . import models


admin.site.register(models.BuildJob)
admin.site.register(models.TestJob)
