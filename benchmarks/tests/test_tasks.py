from django.test import TestCase
from django_dynamic_fixture import G, N
from mock import patch
from django.core import mail
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import re

import django.core.mail

from benchmarks.models import Benchmark
from benchmarks.models import BenchmarkGroup
from benchmarks.models import Environment
from benchmarks.models import Result
from benchmarks.models import ResultData
from benchmarks.models import TestJob
from benchmarks.testminer import LavaServerException

from benchmarks.tasks import set_testjob_results
from benchmarks.tasks import report_email
from benchmarks.tasks import report_gerrit
from benchmarks.tasks import store_testjob_data

from benchmarks.progress import Progress
from benchmarks.tasks import daily_benchmark_progress
from benchmarks.tasks import weekly_benchmark_progress
from benchmarks.tasks import monthly_benchmark_progress

from benchmarks.tests import get_file


from benchmarks.testing import MANIFEST


def lava_xmlrpc_503(jid):
    raise LavaServerException('http://example.com/', 503)


def lava_xmlrpc_502(jid):
    raise LavaServerException('http://example.com/', 502)


def set_status(status):
    def f(testjob):
        testjob.status = status
    return f


def populate_successful_job(job):
    job.status = 'Complete'
    job.completed = True
    job.definition = '{ "metadata" : { "foo": "bar" } }'

    test_results = [
        {
            "board": "good-board",
            "benchmark_name": "MyBenchmark",
            "subscore": [
                {
                    "name": "MyBenchmark1",
                    "measurement": 1.5,
                },
                {
                    "name": "MyBenchmark1",
                    "measurement": 1.7,
                },
                {
                    "name": "MyBenchmark2",
                    "measurement": 3.0,
                },
                {
                    "name": "MyBenchmark2",
                    "measurement": 3.2,
                },
            ]
        },
    ]

    return test_results


class LavaFetchTest(TestCase):

    @patch("benchmarks.tasks.get_testjob_data", lava_xmlrpc_503)
    @patch("benchmarks.models.TestJob.objects.get", lambda **kw: TestJob())
    def test_ignores_lava_503(self):
        set_testjob_results.apply(args=[None])
        # just not crashing is good enough

    @patch("benchmarks.tasks.get_testjob_data", lava_xmlrpc_502)
    @patch("benchmarks.models.TestJob.objects.get", lambda **kw: TestJob())
    def test_ignores_lava_502(self):
        set_testjob_results.apply(args=[None])
        # just not crashing is good enough

    @patch("benchmarks.tasks.get_testjob_data", set_status("Complete"))
    def test_set_testjob_result_saves_testjob(self):
        result = G(Result, manifest=MANIFEST())
        testjob = G(TestJob, result=result, status='Submitted')
        set_testjob_results.apply(args=[testjob.id])

        testjob_from_db = TestJob.objects.get(pk=testjob.id)
        self.assertEqual("Complete", testjob_from_db.status)


    @patch("benchmarks.tasks.get_testjob_data", populate_successful_job)
    def test_dont_duplicate_test_results(self):
        result = G(Result, manifest=MANIFEST())
        testjob = G(TestJob, result=result, status='Submitted')

        set_testjob_results.apply(args=[testjob.id])
        set_testjob_results.apply(args=[testjob.id])

        self.assertEqual(2, result.data.count())


class FakeGerrit(object):
    def __init__(self):
        self.__reports__ = []
    def report(self, current, message):
        self.__reports__.append((current, message))
    @property
    def reports(self):
        return self.__reports__
    def clear(self):
        self.__reports__ = []


fake_gerrit = FakeGerrit()


class ReportsTest(TestCase):

    def setUp(self):
        self.now = timezone.now()
        self.past = self.now - relativedelta(days=1)
        self.baseline = G(
            Result,
            manifest=MANIFEST(),
            branch_name='master',
            gerrit_change_number=None,
            created_at=self.past
        )
        self.current = G(
            Result,
            manifest=MANIFEST(),
            branch_name='master',
            gerrit_change_number=123,
            gerrit_change_id='I8adbccfe4b39a1e849b5d7a976fd4cdc',
            created_at=self.now
        )
        benchmark1 = G(Benchmark)
        G(
            ResultData,
            result=self.baseline,
            benchmark=benchmark1,
            name="benchmark1",
            measurement=5
        )
        G(
            ResultData,
            result=self.current,
            benchmark=benchmark1,
            name="benchmark1",
            measurement=6
        )

        fake_gerrit.clear()

    def test_report_email(self):
        report_email.apply(args=[self.current])
        self.assertEqual(1, len(mail.outbox))

    @patch('benchmarks.gerrit.update', fake_gerrit.report)
    def test_report_gerrit(self):
        report_gerrit.apply(args=[self.current])
        self.assertTrue('branch:' in fake_gerrit.reports[0][1])

class StoreTestJobData(TestCase):

    def test_result_data(self):
        result = G(Result, manifest=MANIFEST())
        testjob = N(TestJob, result=result, status='Complete')
        test_results = [
            {
                'benchmark_name': 'bar',
                'subscore': [
                    { 'name': 'test1', 'measurement': 1 },
                    { 'name': 'test1', 'measurement': 2 },
                ]
            },
        ]
        store_testjob_data(testjob, test_results)

        self.assertEqual(TestJob.objects.count(), 1)
        self.assertEqual(Benchmark.objects.count(), 1)
        self.assertEqual(ResultData.objects.count(), 1)

        result_data = ResultData.objects.order_by('id').last()
        self.assertEqual(result_data.values, [1,2])
        self.assertEqual(result_data.benchmark.name, 'bar')

    def test_result_data_with_benchmark_group(self):
        result = G(Result, manifest=MANIFEST())
        testjob = N(TestJob, result=result, status='Complete')
        test_results = [
            {
                'benchmark_group': 'foo',
                'benchmark_name': 'bar',
                'subscore': [
                    { 'name': 'test1', 'measurement': 1 },
                    { 'name': 'test1', 'measurement': 2 },
                ]
            },
        ]


        store_testjob_data(testjob, test_results)
        self.assertEqual(BenchmarkGroup.objects.count(), 2)  # foo + /

        benchmark_group = BenchmarkGroup.objects.order_by('id').last()
        benchmark = Benchmark.objects.order_by('id').last()
        self.assertEqual(benchmark.group, benchmark_group)

class BenchmarkProgressTasksTest(TestCase):

    def setUp(self):
        self.now = timezone.now()

    def __create_jobs__(self, past, **kwargs):
        build1 = G(
            Result,
            manifest=MANIFEST(),
            branch_name='master',
            name='myproject',
            gerrit_change_number=None,
            created_at=past,
        )
        build2 = G(
            Result,
            manifest=MANIFEST(),
            branch_name="master",
            name='myproject',
            gerrit_change_number=None,
            created_at=timezone.now(),
        )

        env = G(Environment)

        job1 = G(
            TestJob,
            result=build1,
            environment=env,
            completed=True,
            created_at=build1.created_at
        )
        job1.data = get_file("then.json")
        job1.save()


        job2 = G(
            TestJob,
            result=build2,
            environment=env,
            completed=True,
            created_at=build2.created_at
        )
        job2.data = get_file("now.json")
        job2.save()

        progress = Progress("myproject", "master", env, job1, job2)
        return [progress]

    def test_benchmark_progress_daily(self):
        self.__create_jobs__(self.now - relativedelta(days=2))
        daily_benchmark_progress.apply()
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_benchmark_progress_weekly(self):
        self.__create_jobs__(self.now - relativedelta(days=8))
        weekly_benchmark_progress.apply()
        self.assertEqual(len(django.core.mail.outbox), 1)

    def test_benchmark_progress_monthly(self):
        self.__create_jobs__(self.now - relativedelta(days=32))
        monthly_benchmark_progress.apply()
        self.assertEqual(len(django.core.mail.outbox), 1)
