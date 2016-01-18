import hashlib
import xml.etree.ElementTree as ET

from django.db import models
from django.conf import settings


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

    class Meta:
        ordering = ['-id']

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
    id = models.CharField(primary_key=True, max_length=99)

    manifest = models.ForeignKey(Manifest, related_name="results", null=True)

    name = models.CharField(max_length=128)

    branch_name = models.CharField(max_length=128, blank=True)
    build_url = models.URLField()
    build_number = models.IntegerField()

    gerrit_change_number = models.IntegerField(blank=True, null=True)
    gerrit_patchset_number = models.IntegerField(blank=True, null=True)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class TestJob(models.Model):
    result = models.ForeignKey('Result', related_name="test_jobs")

    id = models.CharField(primary_key=True, max_length=100)

    url = models.URLField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(blank=True, default="", max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    definition = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s %s' % (self.id, self.result)


class ResultData(models.Model):
    name = models.CharField(max_length=256)
    benchmark = models.ForeignKey(Benchmark, related_name="data")
    measurement = models.FloatField()
    result = models.ForeignKey(Result, related_name="data")
    board = models.CharField(default="default", max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{0} - {1}".format(self.benchmark, self.name)
