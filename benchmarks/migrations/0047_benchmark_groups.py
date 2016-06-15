# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0046_create_environments_retroactively'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='benchmark',
            name='group',
            field=models.ForeignKey(related_name='benchmarks', to='benchmarks.BenchmarkGroup', null=True),
        ),
    ]
