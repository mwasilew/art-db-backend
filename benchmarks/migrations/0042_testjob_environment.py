# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0041_environment'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='environment',
            field=models.ForeignKey(related_name='test_jobs', to='benchmarks.Environment', null=True),
        ),
    ]
