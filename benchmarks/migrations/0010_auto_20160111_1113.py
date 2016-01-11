# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0009_auto_20160105_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='reduced_hash',
            field=models.CharField(default=None, max_length=40, editable=False),
        ),
    ]
