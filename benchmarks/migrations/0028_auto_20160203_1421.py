# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0027_auto_20160202_1303'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='result',
            index_together=set([('build_id', 'name')]),
        ),
    ]
