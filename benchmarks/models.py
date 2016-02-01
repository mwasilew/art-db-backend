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

    def _get_first(self, query):
        for item in query:
            if item.data.count():
                return item
        return None

    def compare(self, first, second):
        measurement_previous = {d.name: d for d in second.data.select_related("benchmark")}

        results = []

        for resultdata in first.data.order_by("name").select_related("benchmark"):
            current = resultdata
            previous = measurement_previous.get(resultdata.name)

            if previous.measurement:
                change = current.measurement / previous.measurement * 100
                change = (change - 100) * -1

            results.append({
                "current": current,
                "previous": previous,
                "change": change
            })

        return results

    def compare_progress(self, now, interval):
        then = now - interval

        branches = (Result.objects.order_by('branch_name')
                    .distinct("branch_name")
                    .values_list("branch_name", flat=True))

        results_by_branch = {}

        for branch_name in branches:
            query = (Result.objects
                     .order_by("-created_at")
                     .filter(gerrit_change_number__isnull=True,
                             branch_name=branch_name))

            current = self._get_first(
                query.filter(created_at__gt=then, created_at__lte=now))

            previous = self._get_first(
                query.filter(created_at__gt=then - interval, created_at__lte=then))

            if not (previous and current):
                continue

            results_by_branch[branch_name] = self.compare(current, previous)

        return results_by_branch


class Result(models.Model):

    objects = ResultManager()

    manifest = models.ForeignKey(Manifest, related_name="results", null=True)

    name = models.CharField(max_length=128)
    branch_name = models.CharField(max_length=128, blank=True)

    build_url = models.URLField()
    build_number = models.IntegerField()
    build_id = models.IntegerField()

    gerrit_change_number = models.IntegerField(blank=True, null=True)
    gerrit_patchset_number = models.IntegerField(blank=True, null=True)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)

    completed = models.BooleanField(default=False)
    reported = models.BooleanField(default=False)

    def to_compare(self):
        if self.gerrit_change_number:
            return self._default_manager.filter(
                branch_name=self.branch_name,
                gerrit_change_number=None,
                manifest__reduced_hash=self.manifest.reduced_hash
            ).first()
        return None

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class TestJob(models.Model):
    result = models.ForeignKey('Result', related_name="test_jobs")

    id = models.CharField(primary_key=True, max_length=100, blank=False)

    url = models.URLField(blank=True, null=True)
    status = models.CharField(blank=True, default="", max_length=16)
    definition = models.TextField(blank=True, null=True)
    initialized = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    data = models.FileField(null=True)
    testrunnerclass = models.CharField(blank=True, default="GenericLavaTestSystem", max_length=128)
    testrunnerurl = models.CharField(blank=True, default="https://validation.linaro.org/", max_length=256)

    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super(TestJob, self).save(*args, **kwargs)
        test_jobs = self.result.test_jobs
        self.result.completed = (test_jobs.count() == test_jobs.filter(completed=True).count())
        self.result.save()

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return '<%s %s#%s %s>' % (self.id, self.result.build_id, self.result.name, self.status)


class Benchmark(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class ResultData(models.Model):
    result = models.ForeignKey(Result, related_name="data")
    benchmark = models.ForeignKey(Benchmark, related_name="data")

    name = models.CharField(max_length=256)
    board = models.CharField(default="default", max_length=128)
    measurement = models.FloatField(default=0)
    stdev = models.FloatField(default=0)

    values = ArrayField(models.FloatField(), default=list)

    created_at = models.DateTimeField(default=timezone.now)

    def _mean(self, data):
        n = len(data)
        if n < 1:
            return 0
        return sum(data)/float(n)

    def _ss(self, data):
        c = self._mean(data)
        ss = sum((x-c)**2 for x in data)
        return ss

    def _stddev(self, data):
        n = len(data)
        if n < 2:
            return 0
        ss = self._ss(data)
        pvar = ss/n
        return pvar**0.5

    def save(self, *args, **kwargs):
        if self.measurement and not self.values:
            self.values = [self.measurement]

        if self.values:
            self.measurement = self._mean(self.values)
            self.stdev = self._stddev(self.values)

        return super(ResultData, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return "%s - %s: %s" % (self.benchmark, self.name, self.measurement)
