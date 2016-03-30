# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


import re


def fix_build_names(apps, schema_editor):
    Result = apps.get_model("benchmarks", "Result")
    for result in Result.objects.all():
        if re.match('https?://', result.name):
            result.name = re.sub('https?://.*/job/(.*)/[0-9]+/?', '\\1', result.name)
            result.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0031_auto_20160208_1419'),
    ]

    operations = [
        migrations.RunPython(fix_build_names),
    ]
