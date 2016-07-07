# -*- coding: utf-8 -*-

import sys
import urlparse
from django.core.management.base import BaseCommand


from benchmarks.tasks import store_testjob_data
from benchmarks.models import ResultData, Benchmark, BenchmarkGroupSummary, TestJob


def step(s):
    sys.stdout.write(s)
    sys.stdout.flush()


finish = lambda: step('\n')


class Command(BaseCommand):

    def handle(self, *args, **options):
        ResultData.objects.all().delete()
        Benchmark.objects.all().delete()
        BenchmarkGroupSummary.objects.all().delete()

        errors = []

        for testjob in TestJob.objects.all():
            if testjob.data:
                try:
                    data = testjob.data.file.read()
                    tester = testjob.get_tester()
                    test_results = tester.parse_test_results(data)
                    testjob.results_loaded = False
                    store_testjob_data(testjob, test_results)
                    step('.')
                except IOError as ex:
                    step('F')
                    errors.append('%s FAILED (%s)' % (testjob.id,ex))

        finish()
        if errors:
            print('')
            print('Errors:')
            print('-------')
            print('')
            for error in errors:
                print(error)
