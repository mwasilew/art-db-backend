# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0019_auto_20160113_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resultdata',
            old_name='timestamp',
            new_name='created_at',
        ),
    ]
