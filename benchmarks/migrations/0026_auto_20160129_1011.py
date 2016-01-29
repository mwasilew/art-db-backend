# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models



def migrate(apps, schema_editor):
    ResultData = apps.get_model("benchmarks", "ResultData")
    for resultdata in ResultData.objects.all():
        resultdata.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0025_auto_20160129_1011'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
