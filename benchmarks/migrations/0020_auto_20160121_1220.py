# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0019_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testjob',
            name='data',
            field=models.FileField(null=True, upload_to=b''),
        ),
    ]
