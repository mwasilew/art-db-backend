# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0030_auto_20160208_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manifest',
            name='reduced_hash',
        ),
        migrations.AlterField(
            model_name='manifest',
            name='reduced',
            field=models.ForeignKey(related_name='manifests', to='benchmarks.ManifestReduced', null=True),
        ),
    ]
