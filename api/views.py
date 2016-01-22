from itertools import groupby

from django.db.models import Avg, StdDev, Count

from rest_framework import views
from rest_framework import viewsets
from rest_framework import response
from rest_framework import mixins
from rest_framework import status
from rest_framework import filters
from rest_framework.decorators import detail_route
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import list_route

from benchmarks import models as benchmarks_models
from benchmarks import tasks

from . import serializers


# no statistics module in Python 2
def mean(data):
    n = len(data)
    if n < 1:
        return 0
    return sum(data)/float(n)

def _ss(data):
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data):
    n = len(data)
    if n < 2:
        return 0
    ss = _ss(data)
    pvar = ss/n
    return pvar**0.5


class TokenViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Token.objects.all()
    serializer_class = serializers.TokenSerializer

    def list(self, request, pk=None):
        serializer = self.serializer_class(Token.objects.get(user=request.user))
        return response.Response(serializer.data)


class ManifestViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = benchmarks_models.Manifest.objects.prefetch_related("results")

    serializer_class = serializers.ManifestSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('id', 'manifest_hash', 'reduced_hash')


# benchmark
class BenchmarkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = benchmarks_models.Benchmark.objects.all()
    serializer_class = serializers.BenchmarkSerializer
    filter_fields = ('id', 'name')
    pagination_class = None


class BuildViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = benchmarks_models.Result.objects.order_by('name').distinct('name')
    serializer_class = serializers.BuildSerializer
    pagination_class = None


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = benchmarks_models.Result.objects.order_by('branch_name').distinct('branch_name')
    serializer_class = serializers.BranchSerializer
    pagination_class = None


class StatsViewSet(viewsets.ModelViewSet):
    queryset = (benchmarks_models.ResultData.objects
                .select_related("result", "benchmark")
                .order_by('created_at'))

    permission_classes = [DjangoModelPermissions]
    serializer_class = serializers.ResultDataSerializer
    pagination_class = None

    def get_queryset(self):
        branch = self.request.query_params.get('branch')
        benchmarks = self.request.query_params.getlist('benchmark')

        if not (benchmarks and branch):
            return self.queryset.none()

        return self.queryset.filter(benchmark__name__in=benchmarks,
                                    result__branch_name=branch)

# result
class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = (benchmarks_models.Result.objects
                .select_related('manifest')
                .prefetch_related('test_jobs'))
    serializer_class = serializers.ResultSerializer

    filter_backends = (filters.SearchFilter,)
    search_fields = ('id',
                     'branch_name',
                     'name',
                     'build_number',
                     'build_id',
                     'gerrit_change_number',
                     'gerrit_patchset_number',
                     'gerrit_change_url',
                     'gerrit_change_id',
                     'manifest__manifest_hash',
                     'manifest__reduced_hash')

    @detail_route()
    def benchmarks(self, request, pk=None):
        result = self.get_object()
        benchmarks = (benchmarks_models.ResultData.objects
                      .filter(result=result)
                      .select_related("benchmark"))

        serializer = serializers.ResultDataSerializer(benchmarks, many=True)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = benchmarks_models.Result.objects.get(
                build_id=serializer.data['build_id'],
                build_number=serializer.data['build_number']
            )

            serializer = self.get_serializer(instance=result, data=request.data)
            serializer.is_valid(raise_exception=True)

            result.test_jobs.all().delete()
            result.data.all().delete()

        except benchmarks_models.Result.DoesNotExist:
            pass

        result = serializer.save()

        if request.data.get('test_jobs'):

            test_jobs = {item.strip() for item in request.data.get('test_jobs').split(",")}

            for testjob_id in test_jobs:

                testjob = benchmarks_models.TestJob.objects.create(
                    result=result,
                    id=testjob_id
                )
                tasks.set_testjob_results.delay(testjob)

        return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class TestJobViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = benchmarks_models.TestJob.objects.all()
    serializer_class = serializers.TestJobSerializer

    lookup_value_regex = "[^/]+" # LAVA ids are 000.0


# result data
class ResultDataViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    queryset = benchmarks_models.ResultData.objects.all()
    serializer_class = serializers.ResultDataSerializer
    filter_fields = ('id',
        'benchmark',
        'result',
        'created_at')


class ResultDataForManifest(views.APIView):
    """
    Class for showing all results for set parameters:
     - manifest
     - gerrit change ID/number/patchset
    """
    def get_queryset(self):
        queryset = benchmarks_models.ResultData.objects.all()
        manifest = self.request.query_params.get('manifest_id', None)
        gerrit_change_id = self.request.query_params.get('gerrit_change_id', None)
        gerrit_change_number = self.request.query_params.get('gerrit_change_number', None)
        gerrit_patchset_number = self.request.query_params.get('gerrit_patchset_number', None)

        print manifest
        print gerrit_change_id
        print gerrit_change_number
        print gerrit_patchset_number

        results = benchmarks_models.Result.objects.all()
        if manifest:
            results = results.filter(manifest__id=manifest)
        if gerrit_change_id:
            results = results.filter(gerrit_change_id=gerrit_change_id)
        results = results.filter(gerrit_change_number=gerrit_change_number)
        results = results.filter(gerrit_patchset_number=gerrit_patchset_number)
        if gerrit_change_number is None \
            and gerrit_patchset_number is None \
            and gerrit_change_id is None \
            and manifest is None:
            # get results for latest available manifest baseline
            manifest = benchmarks_models.Manifest.objects.latest("id").pk
            results = results.filter(manifest__id=manifest)

        # All result data that matches manifest and/or gerrit
        queryset = queryset.filter(result__in=results)
        print queryset.all()
        return queryset

    def get(self, request, format=None):
        results = []
        metadata = {}
        ret = {
            "data": results,
            "metadata": metadata
        }
        queryset = self.get_queryset()
        results_objects = benchmarks_models.Result.objects.filter(data__in=queryset)
        branches = results_objects.values_list("branch__name").distinct()
        if len(branches) == 1:
            # there should be only one
            metadata['branch'] = branches[0][0]
        manifests = results_objects.values_list("manifest__id").distinct()
        if len(manifests) == 1:
            # there should be only one
            metadata['manifest'] = manifests[0][0]
        boards = results_objects.values_list("board__displayname").distinct()
        metadata['boards'] = [x[0] for x in boards]
        build_urls = results_objects.values_list("build_url").distinct()
        metadata['builds'] = [x[0] for x in build_urls]

        gerrit_change_numbers = results_objects.values_list("gerrit_change_number").distinct()
        gerrit_patchset_numbers = results_objects.values_list("gerrit_patchset_number").distinct()
        if len(gerrit_patchset_numbers) == 1 and \
            len(gerrit_change_numbers) == 1:
                if gerrit_patchset_numbers[0][0] is not None and \
                    gerrit_change_numbers[0][0] is not None:
                    metadata['gerrit'] = "%s/%s" % (gerrit_change_numbers[0][0], gerrit_patchset_numbers[0][0])

        benchmark_name_list = queryset.values_list('benchmark__name').distinct()
        for benchmark in benchmark_name_list:
            res_list = queryset.filter(benchmark__name=benchmark[0])
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
                results.append(subscore_dict)
        return response.Response(ret)


class CompareResults(viewsets.ViewSet):

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

                base_avg = mean(values)
                base_stddev = stddev(values)

                if target and scorename in target:
                    target_items = target[scorename]
                    target_avg = mean(target_items)
                    target_stddev = stddev(target_items)
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

        base_query = benchmarks_models.ResultData.objects.filter(result__branch_name=branch_1)

        target_query = benchmarks_models.ResultData.objects.filter(result__branch_name=branch_2)

        data = self.compare_query(base_query, target_query)

        return response.Response(data)

    @list_route()
    def manifest(self, request):
        manifest_1 = request.query_params.get('manifest_1')
        manifest_2 = request.query_params.get('manifest_2')

        if not (manifest_1 and manifest_2):
            return response.Response([])

        base_query = (benchmarks_models.ResultData.objects
                      .filter(result__manifest__manifest_hash=manifest_1)
                      .select_related('benchmark'))

        target_query = (benchmarks_models.ResultData.objects
                        .filter(result__manifest__manifest_hash=manifest_2)
                        .select_related('benchmark'))

        data = self.compare_query(base_query, target_query)

        return response.Response(data)
