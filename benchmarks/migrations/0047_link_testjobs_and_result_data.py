# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from benchmarks.tasks import store_testjob_data
from benchmarks.testminer import get_tester


def migrate(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    ResultData = apps.get_model('benchmarks', 'ResultData')
    ResultData.objects.all().delete()
    Benchmark = apps.get_model('benchmarks', 'Benchmark')
    for testjob in TestJob.objects.all():
        if testjob.data:
            try:
                data = testjob.data.file.read()
                tester = get_tester(testjob)
                test_results = tester.parse_test_results(data)
                testjob.results_loaded = False
                store_testjob_data(testjob, test_results, ResultData=ResultData, Benchmark=Benchmark)
            except IOError:
                pass # file does not exists os is not readable


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0046_create_environments_retroactively'),
    ]

    operations = [
        migrations.RunPython(
            migrate,
            reverse_code=reverse,
        )
    ]
