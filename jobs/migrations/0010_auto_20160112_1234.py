# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_auto_20160112_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildjob',
            name='gerrit_change_id',
            field=models.CharField(default=b'', max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='gerrit_change_number',
            field=models.CharField(default=b'', max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='gerrit_patchset_number',
            field=models.CharField(default=b'', max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='id',
            field=models.CharField(max_length=99, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='testjob',
            name='status',
            field=models.CharField(default=b'', max_length=16, blank=True),
        ),
    ]
