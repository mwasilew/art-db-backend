# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20160105_0931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buildjob',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='testjob',
            options={'ordering': ['-created_at']},
        ),
    ]
