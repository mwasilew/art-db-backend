import hashlib
import xml.etree.ElementTree as ET

from django.db import models
from django.conf import settings

from jobs.models import TestJob


class Board(models.Model):
    displayname = models.CharField(max_length=32)
    display = models.CharField(max_length=32)


class Benchmark(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class Manifest(models.Model):
    manifest_hash = models.CharField(max_length=40, editable=False)
    # sha1 for selected projects in manifest
    # project list is defined in settings
    reduced_hash = models.CharField(max_length=40, editable=False, default=None)
    manifest = models.TextField()

    def __unicode__(self):
        return self.manifest_hash

    def save(self, *args, **kwargs):
        if not self.pk:
            self.manifest_hash = hashlib.sha1(self.manifest).hexdigest()
            doc = ET.fromstring(self.manifest)
            commit_id_hash = hashlib.sha1()
            for project in settings.BENCHMARK_MANIFEST_PROJECT_LIST:
                project_element_list = doc.findall('.//project[@name="%s"]' % project)
                if project_element_list:
                    for project_element in project_element_list:
                        if project_element.tag == "project":
                            commit_id = project_element.get('revision')
                            commit_id_hash.update(commit_id)
            self.reduced_hash = commit_id_hash.hexdigest()
        return super(Manifest, self).save(*args, **kwargs)


class Result(models.Model):
    board = models.ForeignKey(Board, related_name="results")
    branch_name = models.CharField(max_length=128, blank=True)
    revision = models.CharField(max_length=32, blank=True, default="")
    gerrit_change_number = models.IntegerField(blank=True, null=True)
    gerrit_patchset_number = models.IntegerField(blank=True, null=True)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, default="")
    build_url = models.URLField(null=True, blank=True)
    manifest = models.ForeignKey(Manifest, related_name="results", null=True)
    test_job = models.ForeignKey(TestJob, related_name="results", null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class ResultData(models.Model):
    name = models.CharField(max_length=256)
    benchmark = models.ForeignKey(Benchmark, related_name="data")
    measurement = models.FloatField()
    result = models.ForeignKey(Result, related_name="data")

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{0} - {1}".format(self.benchmark, self.name)
