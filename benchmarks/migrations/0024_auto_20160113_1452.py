# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0023_remove_result_test_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='build_url',
            field=models.URLField(default='http://linaro.org'),
            preserve_default=False,
        ),
    ]
