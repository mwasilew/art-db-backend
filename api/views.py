#from django.shortcuts import render
from rest_framework import views
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from benchmarks import models, serializers

# manifest
class ManifestViewSet(viewsets.ModelViewSet):
    """
    Authentication is needed for this methods
    """
    #authentication_classes = (TokenAuthentication,)
    #permission_classes = (IsAuthenticated,)

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


class ResultDataForManifest(views.APIView):
    """
    Class for showing all results for set parameters:
     - manifest
     - gerrit change ID/number/patchset
    """
    def get_queryset(self):
        queryset = ResultData.objects.all()
        manifest = self.request.query_params.get('manifest', None)
        gerrit_change_id = self.request.query_params.get('gerrit_change_id', None)
        gerrit_change_number = self.request.query_params.get('gerrit_change_number', None)
        gerrit_patchset_number = self.request.query_params.get('gerrit_patchset_number', None)
        results = Result.objects.all()
        if manifest:
            results = results.filter(manifest__manifest=manifest)
        results = results.filter(gerrit_change_id=gerrit_change_id)
        results = results.filter(gerrit_change_number=gerrit_change_number)
        results = results.filter(gerrit_patchset_number=gerrit_patchset_number)

        # All result data that matches manifest and/or gerrit
        queryset = queryset.filter(result__in=results)
        return queryset

    def get(self, request, format=None):
        ret = []
        benchmark_name_list = self.get_queryset().values_list('benchmark__name').distinct()
        for benchmark in benchmark_name_list:
            res_list = filtered_result_data.filter(benchmark__name=benchmark[0])
            subscore_name_list = res_list.values_list('name').distinct()
            for subscore in subscore_name_list:
                s = res_list.filter(name=subscore[0])
                avg = s.aggregate(Avg('measurement'))
                stddev = s.aggregate(StdDev('measurement'))
                ret.append({
                    'benchmark': benchmark[0],
                    'subscore': subscore[0],
                    'avg_value': avg,
                    'stddev': stddev
                    })
        return ret
