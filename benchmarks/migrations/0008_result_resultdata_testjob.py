# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0007_auto_20160118_1121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('branch_name', models.CharField(max_length=128, blank=True)),
                ('build_url', models.URLField()),
                ('build_number', models.IntegerField()),
                ('build_id', models.IntegerField()),
                ('gerrit_change_number', models.IntegerField(null=True, blank=True)),
                ('gerrit_patchset_number', models.IntegerField(null=True, blank=True)),
                ('gerrit_change_url', models.URLField(null=True, blank=True)),
                ('gerrit_change_id', models.CharField(default=b'', max_length=42, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('manifest', models.ForeignKey(related_name='results', to='benchmarks.Manifest', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('measurement', models.FloatField()),
                ('board', models.CharField(default=b'default', max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('benchmark', models.ForeignKey(related_name='data', to='benchmarks.Benchmark')),
                ('result', models.ForeignKey(related_name='data', to='benchmarks.Result')),
            ],
        ),
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
