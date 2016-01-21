# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    Model = apps.get_model("benchmarks", "ResultData")

    for item in Model.objects.all():
        item.result = item.testjob.result
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0015_resultdata_result'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
