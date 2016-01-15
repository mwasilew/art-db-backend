from django.contrib import admin

from .models import (
    Manifest,
    Result,
    ResultData,
    TestJob
)


class ManifestAdmin(admin.ModelAdmin):
    readonly_fields=('manifest_hash', 'reduced_hash')

admin.site.register(Manifest, ManifestAdmin)
admin.site.register(Result)
admin.site.register(TestJob)
admin.site.register(ResultData)

