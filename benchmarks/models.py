import hashlib

from django.db import models


class Configuration(models.Model):
    name = models.CharField(max_length=256)


class BoardConfiguration(models.Model):
    name = models.CharField(max_length=256)


class Board(models.Model):
    displayname = models.CharField(max_length=32)
    display = models.CharField(max_length=32)
    configuration = models.ForeignKey(BoardConfiguration, related_name="boards")


class Benchmark(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name


class Manifest(models.Model):
    manifest_hash = models.CharField(max_length=40, editable=False)
    manifest = models.TextField()

    def __unicode__(self):
        return self.hash

    def save(self, *args, **kwargs):
        if not self.pk:
            self.manifest_hash = hashlib.sha1(self.manifest).hexdigest()
        return super(Manifest, self).save(*args, **kwargs)



class Result(models.Model):
    board = models.ForeignKey(Board, related_name="results")
    branch = models.ForeignKey(Branch, related_name="results")
    revision = models.CharField(max_length=32, null=True, blank=True)
    configuration = models.ForeignKey(Configuration, blank=True, null=True) # is it needed ?
    timestamp = models.DateTimeField(null=True)
    gerrit_change_number = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=2)
    gerrit_patchset_number = models.DecimalField(blank=True, null=True, max_digits=9, decimal_places=2)
    gerrit_change_url = models.URLField(blank=True, null=True)
    gerrit_change_id = models.CharField(max_length=42, blank=True, null=True)
    build_url = models.URLField(null=True, blank=True)
    manifest = models.ForeignKey(Manifest, related_name="results", null=True)

    def __unicode__(self):
        return "%s - %s" % (self.pk, self.build_url)


class ResultData(models.Model):
    name = models.CharField(max_length=256)
    benchmark = models.ForeignKey(Benchmark, related_name="data")
    measurement = models.FloatField()
    timestamp = models.DateTimeField(null=True)
    result = models.ForeignKey(Result, related_name="data")

    def __unicode__(self):
        return "{0} - {1}".format(self.benchmark, self.name)
