# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0027_auto_20160113_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='name',
            field=models.CharField(default='test', max_length=128),
            preserve_default=False,
        ),
    ]
