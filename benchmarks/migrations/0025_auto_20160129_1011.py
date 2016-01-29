# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0024_result_reported'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultdata',
            name='stdev',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='resultdata',
            name='measurement',
            field=models.FloatField(default=0),
        ),
    ]
