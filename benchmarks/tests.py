from django.test import TestCase
from django_dynamic_fixture import G
from django.utils import timezone

from benchmarks.models import Result, ResultData
from datetime import timedelta


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class ResultCase(TestCase):

    def test_compare_1(self):

        result_1 = G(Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=timezone.now())

        result_2 = G(Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=timezone.now() - timedelta(days=7))

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


        compare = Result.objects.compare(timezone.now(), timedelta(days=7))

        self.assertEqual(compare['master'][0]['current_value'], 5)
        self.assertEqual(compare['master'][0]['previous_value'], 10)

