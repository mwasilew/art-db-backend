# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0014_auto_20160112_1234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='configuration',
        ),
        migrations.DeleteModel(
            name='BoardConfiguration',
        ),
    ]
