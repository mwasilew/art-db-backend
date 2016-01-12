# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0013_auto_20160112_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='gerrit_change_id',
            field=models.CharField(default=b'', max_length=42, blank=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='revision',
            field=models.CharField(default=b'', max_length=32, blank=True),
        ),
    ]
