# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0032_fix_build_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default=dict),
        ),
    ]
