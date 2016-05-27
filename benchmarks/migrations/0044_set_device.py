# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations, models


from benchmarks.metadata import extract_device


def set_device(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    for testjob in TestJob.objects.all():
        if testjob.definition:
            data = json.loads(testjob.definition)
            device = extract_device(data)
            if device:
                testjob.metadata['device'] = device
                testjob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0043_resultdata_test_job_id'),
    ]

    operations = [
        migrations.RunPython(
            set_device,
            reverse_code=migrations.RunPython.noop,
        )
    ]
