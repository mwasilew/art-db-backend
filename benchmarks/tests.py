from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone

from django_dynamic_fixture import G

from benchmarks.models import Result, ResultData, TestJob


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class ResultTestCase(TestCase):

    def test_complete_1(self):
        result = G(Result, manifest__manifest=MINIMAL_XML)

        self.assertEqual(result.completed, False)

        G(TestJob, result=result, completed=True)
        G(TestJob, result=result, completed=True)

        self.assertEqual(result.completed, True)

    def test_complete_2(self):
        result = G(Result, manifest__manifest=MINIMAL_XML)

        testjob = G(TestJob, result=result, completed=False)

        self.assertEqual(result.completed, False)
        testjob.completed = True
        self.assertEqual(result.completed, False)


class ResultDataTestCase(TestCase):

    def test_compare_1(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        result_1 = G(Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=now)

        result_2 = G(Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=then)

        G(ResultData,
          result=result_1,
          benchmark__name="load",
          name="load-avg",
          measurement=5)

        G(ResultData,
          result=result_2,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        compare = Result.objects.compare_progress(now, timedelta(days=7))

        self.assertEqual(compare['master'][0]['current'].measurement, 5)
        self.assertEqual(compare['master'][0]['previous'].measurement, 10)
        self.assertEqual(compare['master'][0]['change'], 50.0)

    def test_compare_missing_past(self):
        now = timezone.now()

        result = G(Result,
                   manifest__manifest=MINIMAL_XML,
                   branch_name="master",
                   gerrit_change_number=None,
                   created_at=now)

        G(ResultData,
          result=result,
          benchmark__name="load",
          name="load-avg",
          measurement=5)

        compare = Result.objects.compare_progress(now, relativedelta(days=7))

        self.assertEqual(compare, {})

    def test_compare_missing_current(self):
        now = timezone.now()
        then = now - timedelta(days=7)

        result = G(Result,
                   manifest__manifest=MINIMAL_XML,
                   branch_name="master",
                   gerrit_change_number=None,
                   created_at=then)

        G(ResultData,
          result=result,
          benchmark__name="load",
          name="load-avg",
          measurement=5)

        compare = Result.objects.compare_progress(now, relativedelta(days=7))

        self.assertEqual(compare, {})
