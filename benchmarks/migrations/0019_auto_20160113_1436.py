# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0018_remove_result_branch'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Branch',
        ),
        migrations.RenameField(
            model_name='result',
            old_name='timestamp',
            new_name='created_at',
        ),
    ]
