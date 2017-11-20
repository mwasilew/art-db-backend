# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0053_manifest_hash_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='annotation',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
    ]
