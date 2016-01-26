from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone

from django_dynamic_fixture import G

from benchmarks.models import Result, ResultData


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class ResultDateTestCase(TestCase):

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

        compare = ResultData.objects.compare(now, timedelta(days=7))

        self.assertEqual(compare['master'][0]['current'], 5)
        self.assertEqual(compare['master'][0]['previous'], 10)
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

        compare = ResultData.objects.compare(now, relativedelta(days=7))

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

        compare = ResultData.objects.compare(now, relativedelta(days=7))

        self.assertEqual(compare, {})
