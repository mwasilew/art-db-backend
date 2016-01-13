# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0022_remove_result_revision'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='test_job',
        ),
    ]
