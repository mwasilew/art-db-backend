# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0013_auto_20160119_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='initialized',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='testjob',
            name='testrunnerclass',
            field=models.CharField(default=b'GenericLavaTestSystem', max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='testjob',
            name='testrunnerurl',
            field=models.CharField(default=b'https://validation.linaro.org/', max_length=256, blank=True),
        ),
    ]
