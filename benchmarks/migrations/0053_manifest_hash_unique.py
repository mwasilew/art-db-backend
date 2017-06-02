# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0052_result_name_build_id_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='manifest_hash',
            field=models.CharField(unique=True, max_length=40, editable=False),
        ),
    ]
