# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from benchmarks.tasks import store_testjob_data


def migrate(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    ResultData = apps.get_model('benchmarks', 'ResultData')
    Benchmark = apps.get_model('benchmarks', 'Benchmark')

    # act only on the testjobs for which we identified an environment
    testjobs = TestJob.objects.exclude(environment=None)

    # delete result data from the testjobs who have proper environment
    # information
    results_cleared = []
    for testjob in testjobs.prefetch_related('result').all():
        result = testjob.result
        if result.id not in results_cleared:
            result.data.all().delete()
            results_cleared.append(result.id)

    # recreate result data, this time linked back to the testjob that produced
    # it.
    for testjob in testjobs.all():
        if testjob.data:
            try:
                data = testjob.data.file.read()
                tester = testjob.get_tester()
                test_results = tester.parse_test_results(data)
                testjob.results_loaded = False
                store_testjob_data(testjob, test_results, ResultData=ResultData, Benchmark=Benchmark)
            except IOError:
                pass # file does not exists os is not readable


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0047_benchmark_groups'),
    ]

    operations = [
        migrations.RunPython(
            migrate,
            reverse_code=reverse,
        )
    ]
