# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    Model = apps.get_model("benchmarks", "Result")

    for number, item, in enumerate(Model.objects.all(), 1):
        item.id1 = number
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0005_auto_20160118_1104'),
    ]

    operations = [
         migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
