# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20160105_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildjob',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='buildjob',
            name='url',
            field=models.URLField(),
        ),
    ]
