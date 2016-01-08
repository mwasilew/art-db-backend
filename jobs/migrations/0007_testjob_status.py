# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_testjob_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='status',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
    ]
