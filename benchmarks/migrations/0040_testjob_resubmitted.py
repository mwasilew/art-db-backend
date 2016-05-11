# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0039_auto_20160427_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='resubmitted',
            field=models.BooleanField(default=False),
        ),
    ]
