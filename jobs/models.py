from django.db import models


class BuildJob(models.Model):
    id = models.CharField(primary_key=True, max_length=100)

    url = models.URLField(blank=True)
    name = models.CharField(blank=True, max_length=256)

    manifest = models.TextField(blank=True)
    branch_name = models.CharField(blank=True, max_length=256)

    gerrit_change_id = models.CharField(blank=True, max_length=256)
    gerrit_change_number = models.CharField(blank=True, max_length=256)
    gerrit_patchset_number = models.CharField(blank=True, max_length=256)


class TestJob(models.Model):
    build_job = models.ForeignKey('BuildJob')

    id = models.CharField(primary_key=True, max_length=100)
