# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import json

from benchmarks import testminer


def create_environments(apps, schema_editor):
    Environment = apps.get_model('benchmarks', 'Environment')
    TestJob = apps.get_model('benchmarks', 'TestJob')

    for testjob in TestJob.objects.all():
        testerclass = getattr(testminer, testjob.testrunnerclass)
        tester = testerclass(testjob.testrunnerurl)
        environment = tester.get_environment(testjob.metadata, cls=Environment)
        if environment:
            testjob.environment = environment
            testjob.save()


def delete_environments(apps, schema_editor):
    Environment = apps.get_model('benchmarks', 'Environment')
    TestJob = apps.get_model('benchmarks', 'TestJob')

    Environment.objects.all().delete()
    TestJob.objects.update(environment=None)


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0045_reclassify_testjobs'),
    ]

    operations = [
        migrations.RunPython(
            create_environments,
            reverse_code=delete_environments,
        )
    ]
