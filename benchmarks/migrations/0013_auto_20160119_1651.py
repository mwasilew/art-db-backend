# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0012_resultdata_testjob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='resultdata',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='testjob',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
