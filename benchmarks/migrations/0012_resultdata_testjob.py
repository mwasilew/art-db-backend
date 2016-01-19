# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0011_remove_resultdata_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultdata',
            name='testjob',
            field=models.ForeignKey(related_name='benchmarks', default=None, to='benchmarks.TestJob'),
            preserve_default=False,
        ),
    ]
