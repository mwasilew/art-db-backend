from itertools import groupby

from django.db.models import Avg, StdDev, Count

from rest_framework import views
from rest_framework import viewsets
from rest_framework import response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import list_route, detail_route

from benchmarks import models

from . import serializers
from . import permissions


# manifest
class ManifestViewSet(viewsets.ModelViewSet):
    """
    Authentication is needed for this methods
    """
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.Manifest.objects.all()
    serializer_class = serializers.ManifestSerializer
    filter_fields = ('id', 'manifest_hash', 'manifest')


class ReducedManifestViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.Manifest.objects.all()
    serializer_class = serializers.ReducedManifestSerializer
    filter_fields = ('id', 'manifest_hash', 'manifest')


# board
class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.Board.objects.all()
    serializer_class = serializers.BoardSerializer
    filter_fields = ('id', 'displayname')


# board configuration ?
class BoardConfigurationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.BoardConfiguration.objects.all()
    serializer_class = serializers.BoardConfigurationSerializer
    filter_fields = ('id', 'name')


# benchmark
class BenchmarkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.Benchmark.objects.all()
    serializer_class = serializers.BenchmarkSerializer
    filter_fields = ('id', 'name')


# branch
class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = models.Branch.objects.all()
    serializer_class = serializers.BranchSerializer
    filter_fields = ('id', 'name')


# result
class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
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
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
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
        queryset = models.ResultData.objects.all()
        manifest = self.request.query_params.get('manifest_id', None)
        gerrit_change_id = self.request.query_params.get('gerrit_change_id', None)
        gerrit_change_number = self.request.query_params.get('gerrit_change_number', None)
        gerrit_patchset_number = self.request.query_params.get('gerrit_patchset_number', None)
        results = models.Result.objects.all()
        if manifest:
            results = results.filter(manifest__id=manifest)
        if gerrit_change_id:
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
            res_list = self.get_queryset().filter(benchmark__name=benchmark[0])
            subscore_name_list = res_list.values_list('name').distinct()
            for subscore in subscore_name_list:
                s = res_list.filter(name=subscore[0])
                avg = s.aggregate(Avg('measurement'))
                stddev = s.aggregate(StdDev('measurement'))
                length = s.aggregate(Count('measurement'))
                subscore_dict = {
                    'benchmark': benchmark[0],
                    'subscore': subscore[0]
                    }
                subscore_dict.update(avg)
                subscore_dict.update(stddev)
                subscore_dict.update(length)
                ret.append(subscore_dict)
        return response.Response(ret)


class ComapreResults(viewsets.ViewSet):

    #authentication_classes = (TokenAuthentication,)
    #permission_classes = (permissions.IsAdminGroup,)

    # no statistics module in Python 2
    def mean(self, data):
        n = len(data)
        if n < 1:
            return 0
        return sum(data)/float(n)

    def _ss(self, data):
        c = self.mean(data)
        ss = sum((x-c)**2 for x in data)
        return ss

    def stddev(self, data):
        n = len(data)
        if n < 2:
            return 0
        ss = self._ss(data)
        pvar = ss/n
        return pvar**0.5

    def group_resuls(self, query):
        # magic
        return {
            benchmark: {
                score: [i.measurement for i in v]
                for score, v in groupby(values, lambda x: x.name)}
            for benchmark, values in
            groupby(query, lambda x: x.benchmark.name)}

    def compare_query(self, base_query, target_query):
        base_results = self.group_resuls(base_query)
        target_results = self.group_resuls(target_query)

        data = {}

        for benchmark, results in base_results.items():

            scores = {}
            data = {benchmark: scores}

            target = target_results.get(benchmark)

            for scorename, values in results.items():

                base_avg = self.mean(values)
                base_stddev = self.stddev(values)

                if target and scorename in target:
                    target_items = target[scorename]
                    target_avg = self.mean(target_items)
                    target_stddev = self.stddev(target_items)
                    diff_avg = base_avg - target_avg
                    diff_stddev = base_stddev - target_stddev
                else:
                    target_avg = None
                    target_stddev = None
                    diff_avg = None
                    diff_stddev = None

                scores[scorename] = {
                    "avg": {
                        "base": base_avg,
                        "target": target_avg,
                        "diff": diff_avg
                    },
                    "stddev": {
                        "base": base_stddev,
                        "target": target_stddev,
                        "diff": diff_stddev
                    }
                }

        return data

    @list_route()
    def branch(self, request):
        branch_1 = request.query_params.get('branch_1')
        branch_2 = request.query_params.get('branch_2')

        if not (branch_1 and branch_2):
            return response.Response([])

        base_query = (models.ResultData.objects
                      .filter(result__branch__name=branch_1)
                      .select_related('benchmark'))

        target_query = (models.ResultData.objects
                        .filter(result__branch__name=branch_2)
                        .select_related('benchmark'))

        data = self.compare_query(base_query, target_query)

        return response.Response(data)

    @list_route()
    def manifest(self, request):
        manifest_1 = request.query_params.get('manifest_1')
        manifest_2 = request.query_params.get('manifest_2')

        if not (manifest_1 and manifest_2):
            return response.Response([])

        base_query = (models.ResultData.objects
                      .filter(result__manifest__manifest_hash=manifest_1)
                      .select_related('benchmark'))

        target_query = (models.ResultData.objects
                        .filter(result__manifest__manifest_hash=manifest_2)
                        .select_related('benchmark'))

        data = self.compare_query(base_query, target_query)

        return response.Response(data)
