# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0011_auto_20160112_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='test_job',
            field=models.ForeignKey(related_name='results', to='jobs.TestJob', null=True),
        ),
    ]
