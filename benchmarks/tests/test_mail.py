from django.test import TestCase
from django_dynamic_fixture import G
from django.utils import timezone
from dateutil.relativedelta import relativedelta

import django.core.mail

from benchmarks.models import Result, TestJob, Environment, Benchmark, ResultData
from benchmarks import mail
from benchmarks.progress import Progress

from benchmarks.tests import get_file

MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class SendEmailTestCase(TestCase):

    def setUp(self):
        self.now = timezone.now()
        past = self.now - relativedelta(days=1)
        self.current = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=123,
            created_at=self.now,
        )

        self.baseline = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=None,
            created_at=past,
        )
        self.environment = G(Environment)

    def fake_data(self, build, filename="then.json"):

        job = G(
            TestJob,
            result=build,
            environment=self.environment,
            completed=True,
            created_at=build.created_at
        )
        job.data = get_file(filename)
        job.save()


    def test_result_progress(self):
        self.fake_data(self.baseline)
        self.fake_data(self.current, filename="now.json")

        self.assertTrue(self.current.test_jobs.count() > 0)
        self.assertTrue(self.baseline.test_jobs.count() > 0)

        mail.result_progress(self.current, self.baseline)
        self.assertEqual(len(django.core.mail.outbox), 1)

        message = django.core.mail.outbox[0]
        self.assertTrue(message.body.find('benchmark1') > -1)

    def test_result_progress_baseline_missing(self):
        self.fake_data(self.current)
        mail.result_progress_baseline_missing(self.current)
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_result_progress_baseline_no_results(self):
        self.fake_data(self.current)
        mail.result_progress_baseline_no_results(self.current)
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_result_progress_no_results(self):
        mail.result_progress_no_results(self.current)
        self.assertEqual(len(django.core.mail.outbox), 1)

class BenchmarkProgressTest(TestCase):

    def setUp(self):
        self.now = timezone.now()

    def __progress__(self, past, **kwargs):
        build1 = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            name='myproject',
            gerrit_change_number=None,
            created_at=past,
        )
        build2 = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name="master",
            name='myproject',
            gerrit_change_number=None,
            created_at=timezone.now(),
        )

        env = G(Environment, identifier="myenv1")

        job1 = G(TestJob, result=build1, environment=env, completed=True)
        job1.data = get_file("then.json")
        job1.save()


        job2 = G(TestJob, result=build2, environment=env, completed=True)
        job2.data = get_file("now.json")
        job2.save()

        progress = Progress("myproject", "master", env, job1, job2)
        return [progress]

    def test_benchmark_progress_daily(self):
        past = self.now - relativedelta(days=2)
        progress = self.__progress__(past)
        mail.daily_benchmark_progress(self.now, past, progress)
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_benchmark_progress_weekly(self):
        past = self.now - relativedelta(days=8)
        progress = self.__progress__(past)
        mail.weekly_benchmark_progress(self.now, past, progress)
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_benchmark_progress_monthly(self):
        past = self.now - relativedelta(days=32)
        progress = self.__progress__(past)
        mail.monthly_benchmark_progress(self.now, past, progress)
        self.assertEqual(len(django.core.mail.outbox), 1)
