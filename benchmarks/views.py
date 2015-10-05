from django.shortcuts import render
from rest_framework import viewsets
from crayonbox.benchmarks import models

class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = models.Configuration.objects.all()
    serializer_class = serializers.ConfigurationSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all()
    serializer_class = serializers.BoardSerializer


class BenchmarkViewSet(viewsets.ModelViewSet):
    queryset = models.Benchmark.objects.all()
    serializer_class = serializers.BenchmarkSerializer


class BranchViewSet(viewsets.ModelViewSet):
    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer


class ManifestViewSet(viewsets.ModelViewSet):
    queryset = models.Manifest.objects.all()
    serializer_class = serializers.ManifestSerializer


class ResultDataViewSet(viewsets.ModelViewSet):
    queryset = models.ResultData.objects.all()
    serializer_class = serializers.ResultDataSerializer


class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
