# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    Model = apps.get_model("benchmarks", "TestJob")

    for item in Model.objects.all():
        item.url = "https://validation.linaro.org/scheduler/job/" + item.id
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0009_testjob_data'),
    ]

    operations = [
         migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
