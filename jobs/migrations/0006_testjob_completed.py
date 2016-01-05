# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_auto_20160105_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
