# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0049_make_benchmarkgroup_name_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkGroupSummary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_job_id', models.CharField(max_length=100, null=True, db_index=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('measurement', models.FloatField()),
                ('values', django.contrib.postgres.fields.ArrayField(default=list, base_field=models.FloatField(), size=None)),
                ('environment', models.ForeignKey(related_name='progress_data', to='benchmarks.Environment', null=True)),
                ('group', models.ForeignKey(related_name='progress_data', to='benchmarks.BenchmarkGroup')),
                ('result', models.ForeignKey(related_name='progress_data', to='benchmarks.Result')),
            ],
        ),
    ]
