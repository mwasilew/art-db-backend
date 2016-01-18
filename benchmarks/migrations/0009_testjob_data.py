# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0008_result_resultdata_testjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='data',
            field=models.TextField(blank=True),
        ),
    ]
