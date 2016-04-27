# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0038_testjob_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testjob',
            name='data',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='testjob',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default=dict, blank=True),
        ),
    ]
