# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0006_auto_20151026_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='gerrit_change_number',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='gerrit_patchset_number',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
