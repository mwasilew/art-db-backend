# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import xml.etree.ElementTree as ET
import hashlib


def migrate(apps, schema_editor):
    Manifest = apps.get_model('benchmarks', 'Manifest')
    for manifest_obj in Manifest.objects.filter(reduced_hash=None):
        doc = ET.fromstring(manifest_obj.manifest)
        commit_id_hash = hashlib.sha1()
        for project in settings.BENCHMARK_MANIFEST_PROJECT_LIST:
            project_element_list = doc.findall('.//project[@name="%s"]' % project)
            if project_element_list:
                for project_element in project_element_list:
                    if project_element.tag == "project":
                        commit_id = project_element.get('revision')
                        commit_id_hash.update(commit_id)
        manifest_obj.reduced_hash = commit_id_hash.hexdigest()
        manifest_obj.save()
        print "Updated Manifest (%s) with reduced_hash=%s" % (
            manifest_obj.pk,
            commit_id_hash.hexdigest())


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0008_manifest_reduced_hash'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop)
    ]
