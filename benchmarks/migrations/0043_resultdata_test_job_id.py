# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0042_testjob_environment'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultdata',
            name='test_job_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
