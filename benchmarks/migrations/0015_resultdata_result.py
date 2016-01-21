# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0014_auto_20160121_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultdata',
            name='result',
            field=models.ForeignKey(related_name='data', to='benchmarks.Result', null=True),
        ),
    ]
