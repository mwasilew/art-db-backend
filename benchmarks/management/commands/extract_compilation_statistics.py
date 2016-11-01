# -*- coding: utf-8 -*-

import json

from django.core.management.base import BaseCommand

from benchmarks.tasks import store_testjob_data
from benchmarks.testminer import extract_compilation_statistics
from benchmarks.models import ResultData, TestJob


class Command(BaseCommand):

    def handle(self, *args, **options):
        for testjob in TestJob.objects.all():
            # check if compilation statistics for this job already exist
            compilation_statistics_result_data = ResultData.objects.filter(
                benchmark__group__name__startswith="compilation statistics",
                test_job_id=testjob.id
            )
            if compilation_statistics_result_data:
                print "%s skipped" % testjob.id
                continue
            if testjob.data:
                print "%s extracted" % testjob.id
                data = json.loads(testjob.data.read())
                test_result_list = []
                if "compilation statistics" in data.keys():
                    test_result_statistics = data['compilation statistics']
                extract_compilation_statistics(test_result_statistics, test_result_list)
                testjob.results_loaded = False
                store_testjob_data(testjob, test_result_list)
                testjob.data.close()

