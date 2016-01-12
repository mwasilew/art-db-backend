# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_testjob_definition'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildjob',
            name='gerrit_change_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='testjob',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
