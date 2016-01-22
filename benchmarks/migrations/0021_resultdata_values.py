# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0020_auto_20160121_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultdata',
            name='values',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.FloatField(), size=None),
        ),
    ]
