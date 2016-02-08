# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate(apps, schema_editor):
    Manifest = apps.get_model("benchmarks", "Manifest")
    ManifestReduced = apps.get_model("benchmarks", "ManifestReduced")

    for manifest in Manifest.objects.all():
        reduced, _ = ManifestReduced.objects.get_or_create(hash=manifest.reduced_hash)
        manifest.reduced = reduced
        manifest.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0029_auto_20160208_1342'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
