# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0002_auto_20160114_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='board',
        ),
        migrations.AddField(
            model_name='resultdata',
            name='board',
            field=models.CharField(default=b'default', max_length=128),
        ),
        migrations.DeleteModel(
            name='Board',
        ),
    ]
