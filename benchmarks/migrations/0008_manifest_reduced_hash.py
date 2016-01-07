# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0007_auto_20151117_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='reduced_hash',
            field=models.CharField(default=None, max_length=40, editable=False, null=True, blank=True),
        ),
    ]
