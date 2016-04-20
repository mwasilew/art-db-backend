# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def initialize_results_loaded(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    for testjob in TestJob.objects.all():
        testjob.results_loaded = testjob.completed
        testjob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0035_remove_duplicate_benchmark_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='results_loaded',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            initialize_results_loaded,
            reverse_code=migrations.RunPython.noop,
        )

    ]
