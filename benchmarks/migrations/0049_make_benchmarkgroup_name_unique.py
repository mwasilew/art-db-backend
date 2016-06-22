# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import benchmarks.models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0048_index_test_job_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmarkgroup',
            name='name',
            field=models.CharField(unique=True, max_length=128),
        ),
    ]
