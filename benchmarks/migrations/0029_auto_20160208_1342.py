# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0028_auto_20160203_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManifestReduced',
            fields=[
                ('hash', models.CharField(max_length=40, serialize=False, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='manifest',
            name='reduced',
            field=models.ForeignKey(related_name='manifest', to='benchmarks.ManifestReduced', null=True),
        ),
    ]
