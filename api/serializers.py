import json
import ast

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
    group = serializers.CharField(source='group.name', read_only=True)
    class Meta:
        model = benchmarks_models.Benchmark


class ReducedManifestSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Manifest
        fields = ("id", "manifest_hash", "results")
        depth = 2


class TestJobSerializer(serializers.ModelSerializer):
    can_resubmit = serializers.BooleanField()
    data_filetype = serializers.CharField(read_only=True)

    class Meta:
        model = benchmarks_models.TestJob


class ResultManifestSerializer(serializers.CharField):

    class Meta:
        fields = ("id", "manifest_hash")
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
            'reduced_hash': obj.reduced.hash
        }


class ResultSerializer(serializers.ModelSerializer):
    manifest = ResultManifestSerializer()
    permalink = serializers.CharField(read_only=True)
    test_jobs = TestJobSerializer(many=True, read_only=True)
    results = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = benchmarks_models.Result

    def create(self, validated_data):
        benchmark_results = validated_data.pop('results')
        result = super(ResultSerializer, self).create(validated_data)

        for item in benchmark_results:
            benchmark, _ = benchmarks_models.Benchmark.objects.get_or_create(
                name=item['benchmark']
            )
            result.data.create(
                benchmark=benchmark,
                name=item['name'],
                measurement=item['measurement']
            )
        return result


class ManifestResultSerializer(serializers.ModelSerializer):
    permalink = serializers.CharField(read_only=True)

    class Meta:
        model = benchmarks_models.Result


class ManifestSerializer(serializers.ModelSerializer):
    results = ManifestResultSerializer(many=True, read_only=True)
    reduced_hash = serializers.CharField(source='reduced.hash')

    class Meta:
        fields = ("id", "manifest_hash", "reduced_hash", "results")
        model = benchmarks_models.Manifest


class ManifestReducedSerializer(serializers.ModelSerializer):
    manifests = ManifestSerializer(many=True, read_only=True)

    class Meta:
        model = benchmarks_models.ManifestReduced
        # fields = ('hash', 'results')


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
    build_id = serializers.CharField(source='result.build_id', read_only=True)

    class Meta:
        model = benchmarks_models.ResultData


class BenchmarkGroupSummarySerializer(serializers.ModelSerializer):
    result = serializers.CharField(source='result.id', read_only=True)
    build_id = serializers.CharField(source='result.build_id', read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = benchmarks_models.BenchmarkGroupSummary
        fields = ('id', 'name', 'result', 'build_id', 'measurement', 'created_at')
