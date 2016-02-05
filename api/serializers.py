import json

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from benchmarks import models as benchmarks_models


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.
    Usage::
        class MySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
            class Meta:
                model = MyModel
    """
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class BenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Benchmark


class ReducedManifestSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Manifest
        fields = ("id", "manifest_hash", "results")
        depth = 2


class TestJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = benchmarks_models.TestJob


class ResultManifestSerializer(serializers.CharField):

    class Meta:
        fields = ("id", "manifest_hash", "reduced_hash",)
        model = benchmarks_models.Manifest

    def to_internal_value(self, data):
        manifest, _ = benchmarks_models.Manifest.objects.get_or_create(
            manifest=data
        )
        return manifest

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'manifest_hash': obj.manifest_hash,
            'reduced_hash': obj.reduced_hash
        }


class ResultSerializer(serializers.ModelSerializer):
    manifest = ResultManifestSerializer()
    permalink = serializers.CharField(read_only=True)
    test_jobs = TestJobSerializer(many=True, read_only=True)

    class Meta:
        model = benchmarks_models.Result


class ManifestSerializer(serializers.ModelSerializer):
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        fields = ("id", "manifest_hash", "reduced_hash", "results")
        model = benchmarks_models.Manifest


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    class Meta:
        model = Token
        fields = ('key', 'username')


class BuildSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    class Meta:
        model = benchmarks_models.Result
        fields = ('name',)


class BranchSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField()
    class Meta:
        model = benchmarks_models.Result
        fields = ('branch_name',)


class ResultDataSerializer(serializers.ModelSerializer):
    benchmark = serializers.CharField(source='benchmark.name', read_only=True)

    class Meta:
        model = benchmarks_models.ResultData

