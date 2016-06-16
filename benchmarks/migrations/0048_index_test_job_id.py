# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0047_benchmark_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultdata',
            name='test_job_id',
            field=models.CharField(max_length=100, null=True, db_index=True),
        ),
    ]
