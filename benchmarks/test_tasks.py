from django.test import TestCase as DjangoTestCase
from django_dynamic_fixture import G
from unittest import TestCase
from mock import patch
from django.core import mail
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from benchmarks.models import Benchmark
from benchmarks.models import Result
from benchmarks.models import ResultData
from benchmarks.models import TestJob
from benchmarks.testminer import LavaServerException
from benchmarks.tasks import set_testjob_results

from benchmarks.tasks import report_email


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


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
    def test_ignores_lava_503(self):
        set_testjob_results.apply(args=[None])
        # just not crashing is good enough

    @patch("benchmarks.tasks.get_testjob_data", lava_xmlrpc_502)
    def test_ignores_lava_502(self):
        set_testjob_results.apply(args=[None])
        # just not crashing is good enough

    @patch("benchmarks.tasks.get_testjob_data", set_status("Complete"))
    def test_set_testjob_result_saves_testjob(self):
        result = G(Result, manifest__manifest=MINIMAL_XML)
        testjob = G(TestJob, result=result, status='Submitted')
        set_testjob_results.apply(args=[testjob])

        testjob_from_db = TestJob.objects.get(pk=testjob.id)
        self.assertEqual("Complete", testjob_from_db.status)


    @patch("benchmarks.tasks.get_testjob_data", populate_successful_job)
    def test_dont_duplicate_test_results(self):
        result = G(Result, manifest__manifest=MINIMAL_XML)
        testjob = G(TestJob, result=result, status='Submitted')

        set_testjob_results.apply(args=[testjob])
        set_testjob_results.apply(args=[testjob])

        self.assertEqual(2, result.data.count())


class EmailTasksTest(TestCase):

    def test_report_email(self):
        now = timezone.now()
        past = now - relativedelta(days=1)
        baseline = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=None,
            created_at=past
        )
        current = G(
            Result,
            manifest__manifest=MINIMAL_XML,
            branch_name='master',
            gerrit_change_number=123,
            gerrit_change_id='I8adbccfe4b39a1e849b5d7a976fd4cdc',
            created_at=now
        )
        benchmark1 = G(Benchmark)
        G(
            ResultData,
            result=baseline,
            benchmark=benchmark1,
            name="benchmark1",
            measurement=5
        )
        G(
            ResultData,
            result=current,
            benchmark=benchmark1,
            name="benchmark1",
            measurement=6
        )

        report_email.apply(args=[current])
        self.assertEqual(1, len(mail.outbox))
