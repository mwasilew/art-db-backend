# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0004_result_build_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='build_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='id1',
            field=models.IntegerField(null=True),
        ),
    ]
