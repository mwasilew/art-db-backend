# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0006_auto_20160118_1105'),
    ]

    operations = [
        migrations.DeleteModel("testjob"),
        migrations.DeleteModel("resultdata"),
        migrations.DeleteModel("result")
    ]
