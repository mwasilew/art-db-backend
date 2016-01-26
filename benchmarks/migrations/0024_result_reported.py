# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0023_result_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='reported',
            field=models.BooleanField(default=False),
        ),
    ]
