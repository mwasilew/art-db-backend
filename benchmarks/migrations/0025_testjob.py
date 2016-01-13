# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0024_auto_20160113_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestJob',
            fields=[
                ('id', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('completed', models.BooleanField(default=False)),
                ('status', models.CharField(default=b'', max_length=16, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('definition', models.TextField(null=True, blank=True)),
                ('result', models.ForeignKey(related_name='test_jobs', to='benchmarks.Result')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
