# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    Result = apps.get_model("benchmarks", "Result")
    for result in Result.objects.filter(name="linaro-art-tip-build-nexus9-MicroBenchmarks-Baseline"):
        result.gerrit_change_number = None
        result.gerrit_patchset_number = None
        result.gerrit_change_url = None
        result.gerrit_change_id = ""
        result.save()



class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0026_auto_20160129_1011'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
