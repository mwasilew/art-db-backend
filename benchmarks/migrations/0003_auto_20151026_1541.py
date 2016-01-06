# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
from django.db import migrations, models


def migrate(apps, schema_editor):
    Manifest = apps.get_model("benchmarks", "Manifest")

    for manifest in Manifest.objects.filter():
        manifest.hash = hashlib.sha1(manifest.manifest).hexdigest()
        manifest.save()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0002_manifest_hash'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop)
    ]
