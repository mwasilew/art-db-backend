# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildjob',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 5, 9, 31, 42, 468641, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testjob',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 5, 9, 31, 46, 387894, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
