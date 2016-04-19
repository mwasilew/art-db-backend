# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from benchmarks.models import TestJob
from benchmarks.metadata import extract_metadata


def populate_testjob_metadata(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    for testjob in TestJob.objects.all():
        testjob.metadata = extract_metadata(testjob.definition)
        testjob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0033_testjob_metadata'),
    ]

    operations = [
        migrations.RunPython(
            populate_testjob_metadata,
            reverse_code=migrations.RunPython.noop
        ),
    ]
