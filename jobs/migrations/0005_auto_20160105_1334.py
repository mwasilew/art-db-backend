# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_auto_20160105_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testjob',
            name='build_job',
            field=models.ForeignKey(related_name='test_jobs', to='jobs.BuildJob'),
        ),
    ]
