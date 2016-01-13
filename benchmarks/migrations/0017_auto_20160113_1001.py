# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0016_auto_20160113_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='branch_name',
            field=models.CharField(max_length=128, blank=True),
        ),

    ]
