# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0015_auto_20160113_0947'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='configuration',
        ),
        migrations.DeleteModel(
            name='Configuration',
        ),
    ]
