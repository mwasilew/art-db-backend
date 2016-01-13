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


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Board

    def create(self, validated_data):
        board, created = benchmarks_models.Board.objects.get_or_create(**validated_data)
        return board


class BenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Benchmark

    def create(self, validated_data):
        benchmark, created = benchmarks_models.Benchmark.objects.get_or_create(**validated_data)
        return benchmark


class ReducedManifestSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Manifest
        fields = ("id", "manifest_hash", "results")
        depth = 2


class ManifestSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.Manifest

    def create(self, validated_data):
        manifest, _ = benchmarks_models.Manifest.objects.get_or_create(**validated_data)
        return manifest


class ResultDataSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    board = serializers.CharField()

    class Meta:
        model = benchmarks_models.ResultData


class ResultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = benchmarks_models.Result


    def create(self, validated_data):

        if 'board' in validated_data:
            board_name = validated_data['board']
            board, _ = benchmarks_models.Board.objects.get_or_create(
                displayname=board_name,
                display=board_name
            )
            validated_data['board'] = board
        else:
            validated_data['board'] = None

        if 'manifest' in validated_data:
            manifest_content = validated_data['manifest']
            manifest = benchmarks_models.Manifest.create(manifest=manifest_content)
            validated_data['manifest'] = manifest
        else:
            validated_data['manifest'] = None

        return benchmarks_models.Result.objects.create(**validated_data)


class TestJob(serializers.ModelSerializer):
    class Meta:
        model = benchmarks_models.TestJob


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    class Meta:
        model = Token
        fields = ('key', 'username')
