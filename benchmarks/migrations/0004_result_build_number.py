# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0003_auto_20160115_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='build_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
