# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_testjob_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='definition',
            field=models.TextField(null=True, blank=True),
        ),
    ]
