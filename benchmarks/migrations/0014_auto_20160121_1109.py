# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0013_auto_20160119_1651'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='resultdata',
            options={'ordering': ['-created_at']},
        ),
    ]
