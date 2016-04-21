import hashlib
import xml.etree.ElementTree as ET

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField


from benchmarks.metadata import extract_metadata, extract_name


class ManifestReduced(models.Model):
    hash = models.CharField(primary_key=True, max_length=40)

    def __str__(self):
        return self.hash


class Manifest(models.Model):
    reduced = models.ForeignKey(ManifestReduced, related_name="manifests", null=True)

    manifest_hash = models.CharField(max_length=40, editable=False)
    manifest = models.TextField()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.manifest_hash

    def save(self, *args, **kwargs):
        if not self.pk:

            doc = ET.fromstring(self.manifest)
            commit_id_hash = hashlib.sha1()
            for project in settings.BENCHMARK_MANIFEST_PROJECT_LIST:
                project_element_list = doc.findall('.//project[@name="%s"]' % project)
                if project_element_list:
                    for project_element in project_element_list:
                        if project_element.tag == "project":
                            commit_id = project_element.get('revision')
                            commit_id_hash.update(commit_id)

            self.reduced, _ = ManifestReduced.objects.get_or_create(hash=commit_id_hash.hexdigest())
            self.manifest_hash = hashlib.sha1(self.manifest).hexdigest()

        return super(Manifest, self).save(*args, **kwargs)


class ResultManager(models.Manager):

    def _get_first(self, query):
        for item in query:
            if item.data.count():
                return item
        return None

    def compare(self, first, second):
        if not (first.data.count() and second.data.count()):
            return []

        measurement_previous = {d.name: d for d in second.data.select_related("benchmark")}
        results = []

        for resultdata in first.data.order_by("name").select_related("benchmark"):
            current = resultdata
            previous = measurement_previous.get(resultdata.name)

            if previous and previous.measurement:
                change = current.measurement / previous.measurement * 100
                change = (change - 100) * -1
            else:
                change = None

            results.append({
                "current": current,
                "previous": previous,
                "change": change
            })

        return results

    def compare_benchmarks(self, current, previous):
        current_results = {"%s / %s" % (i.benchmark.name, i.name): i.measurement for i in current}
        previous_results = {"%s / %s" % (i.benchmark.name, i.name): i.measurement for i in previous}

        results = []

        for name, current_measurement in current_results.items():
            previous_measurement = previous_results.get(name)

            if previous_measurement:
                change = current_measurement / previous_measurement * 100
                change = (change - 100) * -1
            else:
                change = None

            results.append({
                "name": name,
                "current": current_measurement,
                "previous": previous_measurement,
                "change": change,
            })

        return sorted(results, key=lambda x: x['name'])

    def compare_progress(self, now, interval):
        then = now - interval

        branches = (Result.objects.order_by('branch_name')
                    .distinct("branch_name")
                    .values_list("branch_name", flat=True))

        results_by_branch = {}

        for branch_name in branches:
            query = (ResultData.objects
                     .filter(result__branch_name=branch_name)
                     .filter(result__gerrit_change_number__isnull=True))
            current = (query
                       .filter(result__created_at__gt=then,
                               result__created_at__lte=now)
                       .order_by("benchmark", "name")
                       .distinct("benchmark", "name"))

            previous = (query
                        .filter(result__created_at__gt=then - interval,
                                result__created_at__lte=then)
                        .order_by("benchmark", "name")
                        .distinct("benchmark", "name"))

            if current and previous:
                results_by_branch[branch_name] = self.compare_benchmarks(
                    current, previous
                )
        return results_by_branch


class Result(models.Model):

    objects = ResultManager()

    manifest = models.ForeignKey(Manifest, related_name="results", null=True)

    name = models.CharField(max_length=128)
    branch_name = models.CharField(max_length=128, blank=True)

    build_id = models.IntegerField()
    build_url = models.URLField()
    build_number = models.IntegerField()

    gerrit_change_number = models.IntegerField(blank=True, null=True)
    gerrit_patchset_number = models.IntegerField(blank=True, null=True)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    completed = models.BooleanField(default=False)
    reported = models.BooleanField(default=False)

    class Meta:
        index_together = ["build_id", "name"]
        ordering = ['-created_at']

    @property
    def permalink(self):
        return "%s/#/build/%s" % (settings.URL, self.id)

    __baseline__ = False

    @property
    def baseline(self):
        # basic per-instance caching
        if self.__baseline__ != False:
            return self.__baseline__

        self.__baseline__ = self._default_manager.annotate(
            data_count=Count('data')
        ).filter(
            data_count__gt=0,
            created_at__lt=self.created_at,
            branch_name=self.branch_name,
            gerrit_change_number=None,
            manifest__reduced__hash=self.manifest.reduced.hash
        ).order_by('-created_at').first()

        return self.__baseline__

    def to_compare(self, results=True):
        if self.data.count() and self.baseline:
            return self.baseline
        return None

    @property
    def testjobs_updated(self):
        if not self.updated_at:
            return True
        jobs = self.test_jobs.filter(updated_at__gt=self.updated_at)
        return jobs.exists()

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class TestJob(models.Model):
    result = models.ForeignKey('Result', related_name="test_jobs")

    id = models.CharField(primary_key=True, max_length=100, blank=False)

    name = models.CharField(blank=True, default="", max_length=512)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(blank=True, default="", max_length=16)
    definition = models.TextField(blank=True, null=True)
    initialized = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    data = models.FileField(null=True)
    testrunnerclass = models.CharField(blank=True, default="GenericLavaTestSystem", max_length=128)
    testrunnerurl = models.CharField(blank=True, default="https://validation.linaro.org/", max_length=256)

    results_loaded = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    metadata = HStoreField(default=dict)

    def save(self, *args, **kwargs):
        self.metadata = extract_metadata(self.definition)
        self.name = extract_name(self.definition)
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
