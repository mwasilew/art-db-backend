# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0012_result_test_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='configuration',
            field=models.ForeignKey(related_name='boards', blank=True, to='benchmarks.BoardConfiguration', null=True),
        ),
    ]
