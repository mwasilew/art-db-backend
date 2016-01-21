# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0017_remove_resultdata_testjob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultdata',
            name='result',
            field=models.ForeignKey(related_name='data', to='benchmarks.Result'),
        ),
    ]
