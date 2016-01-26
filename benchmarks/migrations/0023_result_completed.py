# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0022_auto_20160122_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
