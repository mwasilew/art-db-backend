import os
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone
from mock import patch

from django_dynamic_fixture import G

from benchmarks.tests import get_file

from benchmarks.models import Result, ResultData, TestJob, Manifest, Benchmark

from benchmarks.testing import MANIFEST

FULL_MANFIEST = open(os.path.join(os.path.dirname(__file__), 'manifest.xml')).read()


class ManifestTest(TestCase):

    def test_complete_1(self):
        manifest = Manifest.objects.create(manifest=FULL_MANFIEST)

        self.assertEqual(manifest.reduced.hash, '0efe8e2c8c680e488049abc8fd28941fb828bc95')


class ResultTestCase(TestCase):

    def test_complete_1(self):
        result = G(Result, manifest=MANIFEST())

        self.assertEqual(result.completed, False)

        G(TestJob, result=result, completed=True)
        G(TestJob, result=result, completed=True)

        self.assertEqual(result.completed, True)

    def test_complete_2(self):
        result = G(Result, manifest=MANIFEST())

        testjob = G(TestJob, result=result, completed=False)

        self.assertEqual(result.completed, False)
        testjob.completed = True
        self.assertEqual(result.completed, False)

    def test_updated_at_on_creation(self):
        result = G(Result, manifest=MANIFEST())
        self.assertTrue(result.updated_at is not None)

    def test_testjobs_updated(self):

        present = timezone.now()
        past = present - relativedelta(days=1)

        result = G(Result, manifest=MANIFEST())
        testjob = G(TestJob, result=result, completed=False, updated_at=present)

        result.updated_at = past
        self.assertEqual(True, result.testjobs_updated)

        result.updated_at = present
        self.assertEqual(False, result.testjobs_updated)

        result.updated_at = None
        result.testjobs_updated # we are happy it this just doesn't crash


    def test_to_compare_missing_results_current(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        result_1 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=123,
                     created_at=now)

        result_2 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=then)

        G(ResultData,
          result=result_2,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        self.assertEqual(result_1.to_compare(), None)

    def test_to_compare_missing_results_previous(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        result_1 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=123,
                     created_at=now)

        result_2 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=then)

        G(ResultData,
          result=result_1,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        self.assertEqual(result_1.to_compare(), None)

    def test_to_compare(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        result_1 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=123,
                     created_at=now)

        result_2 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=then)

        result_3 = G(Result,
                     manifest=MANIFEST(),
                     branch_name="master",
                     gerrit_change_number=None,
                     created_at=then)

        G(ResultData,
          result=result_1,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        G(ResultData,
          result=result_3,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        self.assertEqual(result_1.to_compare(), result_3)

    def test_to_compare_for_baseline_builds(self):

        now = timezone.now()
        then = now - relativedelta(days=7)

        current_master = G(Result,
                           manifest=MANIFEST(),
                           branch_name="master",
                           gerrit_change_number=None,
                           created_at=now)

        previous_master = G(Result,
                            manifest=MANIFEST(),
                            branch_name="master",
                            gerrit_change_number=None,
                            created_at=then)

        G(ResultData,
          result=current_master,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        G(ResultData,
          result=previous_master,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        self.assertEqual(previous_master, current_master.to_compare())

class TestJobTestCase(TestCase):

    def test_metadata_is_empty_by_default(self):
        job = TestJob()
        self.assertEqual({}, job.metadata)

    def test_can_resubmit_test_single_node(self):
        result = G(Result, manifest=MANIFEST())
        job = TestJob(result=result)
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Complete"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Running"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Incomplete"
        job.save()
        self.assertTrue(job.can_resubmit())
        job.status = "Canceled"
        job.save()
        self.assertTrue(job.can_resubmit())
        job.status = "Results Missing"
        job.save()
        self.assertTrue(job.can_resubmit())

    def test_can_resubmit_test_multi_node_host(self):
        result = G(Result, manifest=MANIFEST())
        job = TestJob(result=result, id="12345.0")
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Complete"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Running"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Incomplete"
        job.save()
        self.assertTrue(job.can_resubmit())
        job.status = "Canceled"
        job.save()
        self.assertTrue(job.can_resubmit())
        job.status = "Results Missing"
        job.save()
        self.assertTrue(job.can_resubmit())

    def test_can_resubmit_test_multi_node_target(self):
        result = G(Result, manifest=MANIFEST())
        job = TestJob(result=result, id="12345.1")
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Complete"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Running"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Incomplete"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Canceled"
        job.save()
        self.assertFalse(job.can_resubmit())
        job.status = "Results Missing"
        job.save()
        self.assertFalse(job.can_resubmit())

    def test_data_filetype(self):
        result = G(Result, manifest=MANIFEST())
        job = G(TestJob, result=result, id="12345.1")
        job.data = get_file('now.json')

        self.assertEqual('json', job.data_filetype)
    def test_data_filetype_no_data(self):
        job = TestJob()
        self.assertEqual(None, job.data_filetype)
