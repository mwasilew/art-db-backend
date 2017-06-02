# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0051_manifestreduced_created_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='result',
            unique_together=set([('build_id', 'name')]),
        ),
    ]
