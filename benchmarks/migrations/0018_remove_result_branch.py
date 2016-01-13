# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    for item in apps.get_model("benchmarks", "Result").objects.all():
        item.branch_name = item.branch.name
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0017_auto_20160113_1001'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='result',
            name='branch',
        ),
    ]
