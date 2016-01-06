# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0004_auto_20151026_1544'),
    ]

    operations = [
        migrations.RenameField(
            model_name='manifest',
            old_name='hash',
            new_name='manifest_hash',
        ),
    ]
