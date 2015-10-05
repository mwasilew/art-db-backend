#from django.shortcuts import render
from rest_framework import viewsets
from benchmarks import models, serializers

# manifest
class ManifestViewSet(viewsets.ModelViewSet):
    queryset = models.Manifest.objects.all()
    serializer_class = serializers.ManifestSerializer
    filter_fields = ('id', 'manifest')


# board
class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all()
    serializer_class = serializers.BoardSerializer
    filter_fields = ('id', 'displayname')


# board configuration ?
class BoardConfigurationViewSet(viewsets.ModelViewSet):
    queryset = models.BoardConfiguration.objects.all()
    serializer_class = serializers.BoardConfigurationSerializer
    filter_fields = ('id', 'name')


# benchmark
class BenchmarkViewSet(viewsets.ModelViewSet):
    queryset = models.Benchmark.objects.all()
    serializer_class = serializers.BenchmarkSerializer
    filter_fields = ('id', 'name')


# branch
class BranchViewSet(viewsets.ModelViewSet):
    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer
    filter_fields = ('id', 'name')


# result
class ResultViewSet(viewsets.ModelViewSet):
    queryset = models.Result.objects.all()
    serializer_class = serializers.ResultSerializer
    filter_fields = ('id',
        'board',
        'branch',
        'timestamp',
        'gerrit_change_number',
        'gerrit_patchset_number',
        'gerrit_change_url',
        'gerrit_change_id',
        'build_url')

# result data
class ResultDataViewSet(viewsets.ModelViewSet):
    queryset = models.ResultData.objects.all()
    serializer_class = serializers.ResultDataSerializer
    filter_fields = ('id',
        'benchmark',
        'result',
        'timestamp')

