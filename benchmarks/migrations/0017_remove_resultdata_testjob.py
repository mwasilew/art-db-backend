# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0016_auto_20160121_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resultdata',
            name='testjob',
        ),
    ]
