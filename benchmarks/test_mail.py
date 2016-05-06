from django.test import TestCase
from django_dynamic_fixture import G
from django.utils import timezone
from dateutil.relativedelta import relativedelta


from benchmarks.models import Result, ResultData, Benchmark
from benchmarks import mail


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class SendEmailTestCase(TestCase):

    def setUp(self):
        now = timezone.now()
        past = now - relativedelta(days=1)
        self.current = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=123,
            created_at=now,
        )

        self.baseline = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=None,
            created_at=past,
        )
        self.benchmark1 = G(Benchmark)
        self.benchmark2 = G(Benchmark)

    def fake_data(self, build, v1=5, v2=5):
        G(ResultData,
          result=build,
          benchmark=self.benchmark1,
          name="load-avg",
          measurement=v1)
        G(ResultData,
          result=build,
          benchmark=self.benchmark2,
          name="cpu-usage",
          measurement=v2)

    def test_result_progress(self):
        self.fake_data(self.baseline, 5, 5)
        self.fake_data(self.current, 6, 6)
        results = Result.objects.compare(self.current, self.baseline)
        mail.result_progress(self.current, results)

    def test_result_progress_baseline_missing(self):
        self.fake_data(self.current)
        mail.result_progress_baseline_missing(self.current)

    def test_result_progress_baseline_no_results(self):
        self.fake_data(self.current)
        mail.result_progress_baseline_no_results(self.current)

    def test_result_progress_no_results(self):
        mail.result_progress_no_results(self.current)
