import hashlib
from mock import patch

from django_dynamic_fixture import G
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from benchmarks import models


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class TestJobTests(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_incomplete(self):
        testjob = G(models.TestJob, id="000", status="Incomplete", result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.data[0]['id'], "111")

        self.assertEqual(models.TestJob.objects.count(), 2)
        self.assertEqual(models.TestJob.objects.filter(id="000").exists(), True)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), True)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_canceled(self):
        testjob = G(models.TestJob, id="000", status="Canceled", result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.data[0]['id'], "111")

        self.assertEqual(models.TestJob.objects.count(), 2)
        self.assertEqual(models.TestJob.objects.filter(id="000").exists(), True)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), True)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_resultsmissing(self):
        testjob = G(models.TestJob, id="000", status="Results Missing", result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.data[0]['id'], "111")

        self.assertEqual(models.TestJob.objects.count(), 2)
        self.assertEqual(models.TestJob.objects.filter(id="000").exists(), True)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), True)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_with_status_completed(self):

        testjob = G(models.TestJob, status='Complete', result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.TestJob.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), False)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_with_status_running(self):

        testjob = G(models.TestJob, status='Running', result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.TestJob.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), False)

    @patch('benchmarks.testminer.GenericLavaTestSystem.call_xmlrpc', lambda *x, **y: "111")
    @patch('benchmarks.tasks.update_jenkins.delay', lambda *x, **y: None)
    @patch('benchmarks.tasks.set_testjob_results.apply', lambda *x, **y: None)
    @patch.dict('django.conf.settings.CREDENTIALS', {'validation.linaro.org': ("hej", "ho")})
    def test_resubmit_with_status_submitted(self):

        testjob = G(models.TestJob, status='Submitted', result__manifest__manifest=MINIMAL_XML)

        response = self.client.get('/api/testjob/%s/resubmit/' % testjob.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(models.TestJob.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.filter(id="111").exists(), False)


class ResultTests(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    def test_get_1(self):
        response = self.client.get('/api/result/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_get_2(self):
        manifest = G(models.Manifest, manifest=MINIMAL_XML)
        G(models.Result, id=123, manifest=manifest)

        response = self.client.get('/api/result/123/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], 123)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_1(self):

        data = {
            'build_url': 'http://linaro.org',
            'build_number': 200,
            'build_id': 20,
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'123',
            'manifest': MINIMAL_XML
        }

        response = self.client.post('/api/result/', data=data)

        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_2(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'123',
            'build_number': 200,
            'build_id': 20,
            'test_jobs': '655839.0, 655838.0, 655838.0',
            'manifest': MINIMAL_XML
        }

        response = self.client.post('/api/result/', data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.count(), 2)

        items = models.TestJob.objects.values_list('id', flat=True)
        self.assertIn('655839.0', items)
        self.assertIn('655838.0', items)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_3(self):

        data_1 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'manifest': MINIMAL_XML,
            'build_number': 200,
            'build_id': 200
        }

        data_2 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'manifest': MINIMAL_XML,
            'build_number': 201,
            'build_id': 201
        }

        response_1 = self.client.post('/api/result/', data=data_1)
        response_2 = self.client.post('/api/result/', data=data_2)

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 201)

        self.assertEqual(models.Result.objects.count(), 2)
        self.assertEqual(models.Manifest.objects.count(), 1)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_4(self):
        build_id = 200
        build_number = 20

        data_1 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'manifest': MINIMAL_XML,
            'build_number': build_number,
            'build_id': build_id
        }

        data_2 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://linaro.org',
            'manifest': MINIMAL_XML,
            'build_number': build_number,
            'build_id': build_id
        }

        response_1 = self.client.post('/api/result/', data=data_1)
        response_2 = self.client.post('/api/result/', data=data_2)

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 201)

        self.assertEqual(models.Result.objects.count(), 1)
        self.assertEqual(models.Manifest.objects.count(), 1)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_5(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'build_number': 200,
            'build_id': 20,
            'manifest': MINIMAL_XML,
            'created_at': '2016-01-06 09:00:01',
            'test_jobs': " 111, 222 "
        }

        response = self.client.post('/api/result/', data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.count(), 2)
        self.assertEqual(response.data['created_at'], '2016-01-06T09:00:01Z')

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_with_results(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'build_number': 200,
            'build_id': 20,
            'manifest': MINIMAL_XML,
            'test_jobs': " 111, 222 ",
            'results': [
                {"benchmark": "benchmark", "name": "load", "measurement": 3},
                {"benchmark": "benchmark", "name": "boot", "measurement": 10}
            ]
        }

        response = self.client.post('/api/result/', data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.ResultData.objects.count(), 2)

        self.assertEqual(models.ResultData.objects.get(name="load").measurement, 3)
        self.assertEqual(models.ResultData.objects.get(name="boot").measurement, 10)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_post_with_results_empty(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'build_number': 200,
            'build_id': 20,
            'manifest': MINIMAL_XML,
            'test_jobs': " 111, 222 ",
            'results': []
        }

        response = self.client.post('/api/result/', data=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.ResultData.objects.count(), 0)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_add_test_jobs_to_existing_result_object(self):

        initial_data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'build_number': 200,
            'build_id': 20,
            'manifest': MINIMAL_XML,
            'created_at': '2016-01-06 09:00:01',
            'test_jobs': " 111, 222 "
        }

        response0 = self.client.post('/api/result/', data=initial_data)
        self.assertEqual(response0.data['created_at'], '2016-01-06T09:00:01Z')

        additional_data = {
            'build_id': 20,
            'name': u'linaro-art-stable-m-build-juno',
            'test_jobs': " 333 "
        }
        response = self.client.post('/api/result/', data=additional_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Result.objects.count(), 1)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.count(), 3)

    @patch('benchmarks.tasks.update_jenkins.delay', lambda x: None)
    @patch('benchmarks.tasks.set_testjob_results.delay', lambda x: None)
    def test_add_existing_test_jobs_to_existing_result_object(self):

        initial_data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'build_number': 200,
            'build_id': 20,
            'manifest': MINIMAL_XML,
            'created_at': '2016-01-06 09:00:01',
            'test_jobs': " 111, 222 "
        }

        response0 = self.client.post('/api/result/', data=initial_data)
        self.assertEqual(response0.data['created_at'], '2016-01-06T09:00:01Z')

        additional_data = {
            'build_id': 20,
            'name': u'linaro-art-stable-m-build-juno',
            'test_jobs': " 111, 222 "
        }
        response = self.client.post('/api/result/', data=additional_data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.Result.objects.count(), 1)
        self.assertEqual(models.Manifest.objects.count(), 1)
        self.assertEqual(models.TestJob.objects.count(), 2)

    def test_baseline_1(self):

        baseline = G(models.Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=None)

        current = G(models.Result,
                    manifest__manifest=MINIMAL_XML,
                    branch_name="master",
                    gerrit_change_number=123)

        G(models.ResultData,
          result=current,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        G(models.ResultData,
          result=baseline,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        response = self.client.get('/api/result/%s/baseline/' % current.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], baseline.id)

    def test_baseline_2(self):

        result_1 = G(models.Result,
                     manifest__manifest=MINIMAL_XML,
                     branch_name="master",
                     gerrit_change_number=123)

        G(models.ResultData,
          result=result_1,
          benchmark__name="load",
          name="load-avg",
          measurement=10)

        response = self.client.get('/api/result/%s/baseline/' % result_1.pk)

        self.assertEqual(response.status_code, 204)


class ManifestTests(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    def test_get_1(self):
        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_get_2(self):
        manifest_hash = hashlib.sha1(MINIMAL_XML).hexdigest()

        models.Manifest.objects.create(manifest=MINIMAL_XML)

        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['manifest_hash'], manifest_hash)

    def test_search(self):
        xml_1 = MINIMAL_XML + " "
        xml_2 = MINIMAL_XML + "  "

        manifest_hash_1 = hashlib.sha1(xml_1).hexdigest()
        manifest_hash_2 = hashlib.sha1(xml_1).hexdigest()

        models.Manifest.objects.create(manifest=xml_1)
        models.Manifest.objects.create(manifest=xml_2)

        response = self.client.get('/api/manifest/?manifest_hash=test')
        self.assertEqual(response.data['count'], 0)

        response = self.client.get('/api/manifest/?manifest_hash=%s' % manifest_hash_1)
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/api/manifest/?manifest_hash=%s' % manifest_hash_2)
        self.assertEqual(response.data['count'], 1)


class CompareTests(APITestCase):

    def setUp(self):
        user = User.objects.create_user('test', None, 'pass')
        user.groups.create(name="admin")
        self.client.force_authenticate(user=user)

    def test_compare_with_manifest_0(self):
        response = self.client.get('/api/compare/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_compare_with_manifest_1(self):

        benchmark = G(models.Benchmark, name="cpu")

        manifest_1 = G(models.Manifest, manifest=MINIMAL_XML)
        manifest_2 = G(models.Manifest, manifest=MINIMAL_XML)

        manifest_1_result = G(models.Result, manifest=manifest_1)
        manifest_2_result = G(models.Result, manifest=manifest_2)

        G(models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",
          values=[10])

        G(models.ResultData,
          result=manifest_2_result,
          benchmark=benchmark,
          name="load",
          values=[2])

        response = self.client.get('/api/compare/manifest/', {
            'manifest_1': manifest_1.manifest_hash,
            'manifest_2': manifest_2.manifest_hash
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertTrue('cpu' in response.data)
        self.assertTrue('load' in response.data['cpu'])
        self.assertTrue('avg' in response.data['cpu']['load'])
        self.assertTrue('stddev' in response.data['cpu']['load'])

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 6.0)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], 6.0)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], 0.0)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 4.0)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], 4.0)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], 0)

    def test_compare_with_branch(self):

        benchmark = G(models.Benchmark, name="cpu")

        branch_1_name = "test1"
        branch_2_name = "test2"

        branch_1_result = G(models.Result,
                            branch_name=branch_1_name,
                            manifest=G(models.Manifest, manifest=MINIMAL_XML))

        branch_2_result = G(models.Result,
                            branch_name=branch_2_name,
                            manifest=G(models.Manifest, manifest=MINIMAL_XML))

        G(models.ResultData,
          result=branch_1_result,
          benchmark=benchmark,
          name="load",
          values=[10])

        G(models.ResultData,
          result=branch_2_result,
          benchmark=benchmark,
          name="load",
          values=[2])

        response = self.client.get('/api/compare/branch/', {
            'branch_1': branch_1_name,
            'branch_2': branch_2_name
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 10)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], 2)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], 8)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], 0)

    def test_compare_missing_benchmark(self):

        benchmark = G(models.Benchmark, name="cpu")

        manifest_1 = G(models.Manifest, manifest=MINIMAL_XML)
        manifest_2 = G(models.Manifest, manifest=MINIMAL_XML)

        manifest_1_result = G(models.Result, manifest=manifest_1)

        G(models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",
          values=[10])

        response = self.client.get('/api/compare/manifest/', {
            'manifest_1': manifest_1.manifest_hash,
            'manifest_2': manifest_2.manifest_hash
        })

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 10)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], 10)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], 0)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], 0)

class StatsTest(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    @patch('django.conf.settings.IGNORE_GERRIT', False)
    def test_missing_parameters(self):
	now = timezone.now()
	yesterday = now - relativedelta(days=1)

	baseline = G(models.Result,
	      manifest__manifest=MINIMAL_XML,
	      branch_name='master',
              name="TheProject",
	      created_at=yesterday,
	      gerrit_change_number=None)

	patched = G(models.Result,
	     manifest__manifest=MINIMAL_XML,
	     branch_name='master',
             name="TheProject",
	     created_at=now,
	     gerrit_change_number=123)

	benchmark = G(models.Benchmark, name="TheBenchmark")

        G(models.ResultData,
          result=baseline,
          benchmark=benchmark,
          name="TheBenchmark",
          measurement=5)

        G(models.ResultData,
          result=patched,
          benchmark=benchmark,
          name="TheBenchmark",
          measurement=10)

        response = self.client.get('/api/stats/', {
            'branch': 'master',
            'benchmark': 'TheBenchmark',
        })

        self.assertEqual(len(response.data), 0)

        response = self.client.get('/api/stats/', {
            'benchmark': 'TheBenchmark',
            'project': 'TheProject',
        })

        self.assertEqual(len(response.data), 0)

        response = self.client.get('/api/stats/', {
            'branch': 'master',
            'project': 'TheProject',
        })

        self.assertEqual(len(response.data), 0)

    @patch('django.conf.settings.IGNORE_GERRIT', False)
    def test_only_baseline_changes(self):

	now = timezone.now()
	yesterday = now - relativedelta(days=1)

	baseline = G(models.Result,
	      manifest__manifest=MINIMAL_XML,
	      branch_name='master',
              name="TheProject",
	      created_at=yesterday,
	      gerrit_change_number=None)

	patched = G(models.Result,
	     manifest__manifest=MINIMAL_XML,
	     branch_name='master',
             name="TheProject",
	     created_at=now,
	     gerrit_change_number=123)

	benchmark = G(models.Benchmark, name="TheBenchmark")
	environment = G(models.Environment, identifier='myenv')
	testjob_baseline = G(models.TestJob, id=u'888888', environment=environment,result=baseline, completed=True)
	testjob_patched = G(models.TestJob, id=u'999999', environment=environment, result=patched, completed=True)

        G(models.ResultData,
          result=baseline,
          benchmark=benchmark,
          test_job_id=testjob_baseline.id,
          name="TheBenchmark",
          measurement=5)

        G(models.ResultData,
          result=patched,
          benchmark=benchmark,
          test_job_id=testjob_patched.id,
          name="TheBenchmark",
          measurement=10)

        response = self.client.get('/api/stats/', {
            'branch': 'master',
            'benchmark': 'TheBenchmark',
            'project': 'TheProject',
            'environment': 'myenv',
        })

        self.assertEqual(len(response.data), 1)
	self.assertEqual(response.data[0]['measurement'], 5)

    @patch('django.conf.settings.IGNORE_GERRIT', True)
    def test_only_baseline_changes_ignore_gerrit(self):

	now = timezone.now()
	yesterday = now - relativedelta(days=1)

	baseline = G(models.Result,
	      manifest__manifest=MINIMAL_XML,
	      branch_name='master',
              name="TheProject",
	      created_at=yesterday,
	      gerrit_change_number=None)

	patched = G(models.Result,
	     manifest__manifest=MINIMAL_XML,
	     branch_name='master',
             name="TheProject",
	     created_at=now,
	     gerrit_change_number=123)

	benchmark = G(models.Benchmark, name="TheBenchmark")
	environment = G(models.Environment, identifier='myenv')
	testjob_baseline = G(models.TestJob, id=u'888888', environment=environment,result=baseline, completed=True)
	testjob_patched = G(models.TestJob, id=u'999999', environment=environment, result=patched, completed=True)

        G(models.ResultData,
          result=baseline,
          benchmark=benchmark,
          test_job_id=testjob_baseline.id,
          name="TheBenchmark",
          measurement=5)

        G(models.ResultData,
          result=patched,
          benchmark=benchmark,
          test_job_id=testjob_patched.id,
          name="TheBenchmark",
          measurement=10)

        response = self.client.get('/api/stats/', {
            'branch': 'master',
            'benchmark': 'TheBenchmark',
            'project': 'TheProject',
            'environment': 'myenv',
        })

        self.assertEqual(len(response.data), 2)
	self.assertEqual(response.data[0]['measurement'], 5)
	self.assertEqual(response.data[1]['measurement'], 10)
