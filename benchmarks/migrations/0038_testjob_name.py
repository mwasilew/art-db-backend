# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0037_updated_at_for_testjob_and_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='testjob',
            name='name',
            field=models.CharField(default=b'', max_length=512, blank=True),
        ),
    ]
