# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


import json
from benchmarks.testminer import GenericLavaTestSystem


def reclassify_testjobs(apps, schema_editor):
    TestJob = apps.get_model('benchmarks', 'TestJob')
    tester = GenericLavaTestSystem('http://example.com/')
    for testjob in TestJob.objects.all():
        if testjob.definition:
            definition = json.loads(testjob.definition)
            class_name = tester.get_result_class_name_from_definition(definition)
            if class_name != testjob.testrunnerclass:
                testjob.testrunnerclass = class_name
                testjob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0044_set_device'),
    ]

    operations = [
        migrations.RunPython(
            reclassify_testjobs,
            reverse_code=migrations.RunPython.noop,
        )
    ]
