# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0036_testjob_results_loaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='testjob',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
