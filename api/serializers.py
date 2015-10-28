from rest_framework import serializers
from benchmarks import models
from datetime import datetime


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


class ConfigurationSerializer(serializers.ModelSerializer, DynamicFieldsMixin):
    class Meta:
        model = models.Configuration


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board

    def create(self, validated_data):
        board, created = models.Board.objects.get_or_create(**validated_data)
        return board


class BoardConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BoardConfiguration

    def create(self, validated_data):
        boardconfig, created = models.BoardConfiguration.objects.get_or_create(**validated_data)
        return boardconfig


class BenchmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Benchmark

    def create(self, validated_data):
        benchmark, created = models.Benchmark.objects.get_or_create(**validated_data)
        return benchmark


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Branch

    def create(self, validated_data):
        branch, created = models.Branch.objects.get_or_create(**validated_data)
        return branch


class ManifestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manifest

    def create(self, validated_data):
        manifest, _ = models.Manifest.objects.get_or_create(**validated_data)
        return manifest


class ResultDataSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.ResultData
        #depth = 1
        #fields = ('id', 'name', 'benchmark', 'measurement', 'timestamp', 'result')

    def create(self, validated_data):
        defaults = {
            "timestamp": datetime.now()
        }
        resultdata, created = models.ResultData.objects.get_or_create(defaults=defaults, **validated_data)
        return resultdata

class ResultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Result
        #depth = 1

    def create(self, validated_data):
        defaults = {
            "timestamp": datetime.now()
        }
        result, created = models.Result.objects.get_or_create(defaults=defaults, **validated_data)
        return result
