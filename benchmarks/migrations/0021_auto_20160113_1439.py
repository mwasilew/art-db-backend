# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0020_auto_20160113_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 13, 14, 39, 30, 179769, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='resultdata',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 13, 14, 39, 33, 547206, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
