# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from benchmarks.models import TestJob


def populate_testjob_metadata(apps, schema_editor):
    for testjob in TestJob.objects.all():
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
