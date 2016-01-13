# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0026_auto_20160113_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='board',
            field=models.ForeignKey(related_name='results', to='benchmarks.Board', null=True),
        ),
    ]
