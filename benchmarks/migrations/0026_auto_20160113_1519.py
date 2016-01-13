# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0025_testjob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='id',
            field=models.CharField(max_length=99, serialize=False, primary_key=True),
        ),
    ]
