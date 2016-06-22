from dateutil.relativedelta import relativedelta
from django_dynamic_fixture import G
from django.test import TestCase
from django.utils import timezone

from benchmarks.models import Result, ResultData
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

        G(ResultData,
          result=result_now,
          benchmark__name="benchmark1",
          name="benchmark1",
          values=[1.1,1.2,1.3,1.2,1.4])

        G(ResultData,
          result=result_then,
          benchmark__name="benchmark1",
          name="benchmark1",
          values=[1,1.1,1.2,1.1,1.3])

        output = render_comparison(result_then.data.all(), result_now.data.all())
        self.assertTrue("benchmark1" in output)
