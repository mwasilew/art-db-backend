# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuildJob',
            fields=[
                ('id', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('url', models.URLField(blank=True)),
                ('name', models.CharField(max_length=256, blank=True)),
                ('manifest', models.TextField(blank=True)),
                ('branch_name', models.CharField(max_length=256, blank=True)),
                ('gerrit_change_id', models.CharField(max_length=256, blank=True)),
                ('gerrit_change_number', models.CharField(max_length=256, blank=True)),
                ('gerrit_patchset_number', models.CharField(max_length=256, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestJob',
            fields=[
                ('id', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('build_job', models.ForeignKey(to='jobs.BuildJob')),
            ],
        ),
    ]
