# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0021_auto_20160113_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='revision',
        ),
    ]
