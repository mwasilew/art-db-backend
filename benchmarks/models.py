import hashlib
import xml.etree.ElementTree as ET

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


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


class ResultManager(models.Manager):
    def compare(self, now, interval):

        branches = (Result.objects.order_by('branch_name')
                    .distinct("branch_name")
                    .values_list("branch_name", flat=True))

        results_by_branch = {}

        for branch_name in branches:
            query = (Result.objects
                     .order_by("-created_at")
                     .filter(gerrit_change_number__isnull=True,
                             branch_name=branch_name))

            current = None

            for item in query.filter(created_at__range=(now - interval, now)):
                if item.data.count():
                    current = item
                    break

            previous = None
            for item in query.filter(created_at__range=(now - interval - interval, now - interval)):
                if item.data.count():
                    previous = item
                    break

            measurement_previous =  {d.name: d.measurement for d in previous.data.all()}

            results = []

            for benchmark in current.data.order_by("name"):
                current_value = benchmark.measurement
                previous_value = measurement_previous.get(benchmark.name)
                change = current_value / previous_value  if previous_value else None

                results.append({
                    "benchmark": benchmark.benchmark.name,
                    "name": benchmark.name,
                    "current_value": current_value,
                    "previous_value": previous_value,
                    "change": change
                })

            results_by_branch[branch_name] = results

        return results_by_branch


class Result(models.Model):
    manifest = models.ForeignKey(Manifest, related_name="results", null=True)

    name = models.CharField(max_length=128)

    branch_name = models.CharField(max_length=128, blank=True)

    build_url = models.URLField()
    build_number = models.IntegerField()
    build_id  = models.IntegerField()

    gerrit_change_number = models.IntegerField(blank=True, null=True)
    gerrit_patchset_number = models.IntegerField(blank=True, null=True)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)

    objects = ResultManager()

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class TestJob(models.Model):
    result = models.ForeignKey('Result', related_name="test_jobs")

    id = models.CharField(primary_key=True, max_length=100)

    url = models.URLField(blank=True, null=True)
    status = models.CharField(blank=True, default="", max_length=16)
    definition = models.TextField(blank=True, null=True)
    initialized = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    data = models.FileField(null=True)
    testrunnerclass = models.CharField(blank=True, default="GenericLavaTestSystem", max_length=128)
    testrunnerurl = models.CharField(blank=True, default="https://validation.linaro.org/", max_length=256)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return '%s %s' % (self.id, self.result)


class Benchmark(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class ResultData(models.Model):
    result = models.ForeignKey(Result, related_name="data")
    benchmark = models.ForeignKey(Benchmark, related_name="data")

    name = models.CharField(max_length=256)
    board = models.CharField(default="default", max_length=128)
    measurement = models.FloatField()

    values = ArrayField(models.FloatField(), default=list)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return "%s - %s: %s" % (self.benchmark, self.name, self.measurement)
