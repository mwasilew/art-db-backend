# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0003_auto_20151026_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='hash',
            field=models.CharField(max_length=40),
        ),
    ]
