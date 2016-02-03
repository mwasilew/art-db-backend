from django.contrib import admin

from .models import Manifest, Result, ResultData, TestJob


@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('manifest_hash', 'reduced_hash')
    readonly_fields = ('manifest_hash', 'reduced_hash')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'build_id', 'name', 'build_number', 'gerrit_change_number',
                    'gerrit_patchset_number', 'gerrit_change_id', 'created_at')


@admin.register(TestJob)
class TestJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'status', 'completed', 'created_at')


@admin.register(ResultData)
class ResultDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'result', 'benchmark', 'board', 'measurement', 'created_at')

    def result(self, obj):
        result = obj.testjob.result
        return "%s#%s/%s" % (result.build_id, result.name, result.build_number)

