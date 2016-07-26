import os
from dateutil.relativedelta import relativedelta
from django_dynamic_fixture import G
from django.test import TestCase
from django.utils import timezone

from benchmarks.tests import get_file
from benchmarks.models import Result, ResultData, TestJob
from benchmarks.comparison import render_comparison

MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class ComparisonTest(TestCase):

    def test_render_comparison(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        result_now = G(Result,
                      name="name1",
                      manifest__manifest=MINIMAL_XML,
                      branch_name="master",
                      gerrit_change_number=None,
                      created_at=now)

        result_then = G(Result,
                      name="name2",
                      manifest__manifest=MINIMAL_XML,
                      branch_name="master",
                      gerrit_change_number=None,
                      created_at=now)

        testjob_now = G(
            TestJob,
            result=result_now,
            completed=True,
        )
        testjob_now.data = get_file("now.json")
        testjob_now.save()

        testjob_then = G(
            TestJob,
            result=result_now,
            completed=True,
        )
        testjob_then.data = get_file("then.json")
        testjob_then.save()

        output = render_comparison(testjob_then, testjob_now)
        self.assertTrue("benchmark1" in output)
