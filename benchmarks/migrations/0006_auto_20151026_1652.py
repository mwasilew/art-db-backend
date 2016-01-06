# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0005_auto_20151026_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='manifest_hash',
            field=models.CharField(max_length=40, editable=False),
        ),
    ]
