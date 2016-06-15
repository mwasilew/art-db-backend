from django.contrib import admin

from .models import Manifest, Result, ResultData, TestJob, Environment, Benchmark, BenchmarkGroup
from .tasks import set_testjob_results

@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = ('manifest_hash', 'reduced')
    readonly_fields = ('manifest_hash', 'reduced')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'build_id', 'name', 'build_number', 'gerrit_change_number',
                    'gerrit_patchset_number', 'gerrit_change_id', 'created_at')


@admin.register(TestJob)
class TestJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'status', 'completed', 'created_at')
    actions = ['force_fetch_results']

    def force_fetch_results(self, request, queryset):
        for testjob in queryset.all():
            testjob.initialized = False
            testjob.completed = False
            testjob.results_loaded = False
            testjob.save()
            set_testjob_results.delay(testjob.id)
    force_fetch_results.short_description = "Force fetch results"

@admin.register(ResultData)
class ResultDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'result', 'benchmark', 'board', 'measurement', 'created_at')

    def result(self, obj):
        result = obj.testjob.result
        return "%s#%s/%s" % (result.build_id, result.name, result.build_number)

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name')
    readonly_fields = ('identifier',)

@admin.register(BenchmarkGroup)
class BenchmarkGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')
