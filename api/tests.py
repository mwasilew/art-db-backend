import hashlib

from django_dynamic_fixture import G
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from benchmarks import models as benchmarks_models


MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'


class ResultTests(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    def test_get_1(self):
        response = self.client.get('/api/result/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_2(self):
        manifest = G(benchmarks_models.Manifest, manifest=MINIMAL_XML)
        G(benchmarks_models.Result, id=123, manifest=manifest)

        response = self.client.get('/api/result/123/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], '123')

    def test_post_1(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'123',
            'manifest': MINIMAL_XML
        }

        response = self.client.post('/api/result/', data=data)

        self.assertEqual(benchmarks_models.Manifest.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

    def test_post_2(self):

        data = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'123',
            'test_jobs': '655839.0, 655838.0',
            'manifest': MINIMAL_XML
        }

        response = self.client.post('/api/result/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(benchmarks_models.Manifest.objects.count(), 1)
        self.assertEqual(benchmarks_models.TestJob.objects.count(), 2)

        items = benchmarks_models.TestJob.objects.values_list('id', flat=True)
        self.assertIn('655839.0', items)
        self.assertIn('655838.0', items)

    def test_post_3(self):

        data_1 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'123',
            'manifest': MINIMAL_XML
        }

        data_2 = {
            'build_url': 'http://linaro.org',
            'name': u'linaro-art-stable-m-build-juno',
            'url': u'http://dynamicfixture1.com',
            'id': u'125',
            'manifest': MINIMAL_XML
        }

        self.assertEqual(self.client.post('/api/result/', data=data_1).status_code, 201)
        self.assertEqual(self.client.post('/api/result/', data=data_2).status_code, 201)

        self.assertEqual(benchmarks_models.Manifest.objects.count(), 1)


class ManifestTests(APITestCase):

    def setUp(self):
        user = User.objects.create_superuser('test', 'email@test.com', 'test')
        self.client.force_authenticate(user=user)

    def test_get_1(self):
        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_2(self):
        manifest_hash = hashlib.sha1(MINIMAL_XML).hexdigest()

        benchmarks_models.Manifest.objects.create(manifest=MINIMAL_XML)

        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['manifest_hash'], manifest_hash)

    def test_post(self):

        response = self.client.post('/api/manifest/',
                                    data={'manifest': MINIMAL_XML})

        self.assertEqual(response.data['manifest_hash'],
                         hashlib.sha1(MINIMAL_XML).hexdigest())

        self.assertEqual(benchmarks_models.Manifest.objects.count(), 1)

        response = self.client.post('/api/manifest/',
                                    data={'manifest': MINIMAL_XML})

        self.assertEqual(response.data['manifest_hash'],
                         hashlib.sha1(MINIMAL_XML).hexdigest())

        self.assertEqual(benchmarks_models.Manifest.objects.count(), 1)


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

        benchmark = G(benchmarks_models.Benchmark, name="cpu")

        manifest_1 = G(benchmarks_models.Manifest, manifest=MINIMAL_XML)
        manifest_2 = G(benchmarks_models.Manifest, manifest=MINIMAL_XML)

        manifest_1_result = G(benchmarks_models.Result, manifest=manifest_1)
        manifest_2_result = G(benchmarks_models.Result, manifest=manifest_2)

        G(benchmarks_models.ResultData,
            result=manifest_1_result,
            benchmark=benchmark,
            name="load",

            measurement=10)

        G(benchmarks_models.ResultData,
          result=manifest_2_result,
          benchmark=benchmark,
          name="load",

          measurement=2)

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

        benchmark = G(benchmarks_models.Benchmark, name="cpu")

        branch_1_name = "test1"
        branch_2_name = "test2"

        branch_1_result = G(benchmarks_models.Result,
                            branch_name=branch_1_name,
                            manifest=G(benchmarks_models.Manifest, manifest=MINIMAL_XML))

        branch_2_result = G(benchmarks_models.Result,
                            branch_name=branch_2_name,
                            manifest=G(benchmarks_models.Manifest, manifest=MINIMAL_XML))

        G(benchmarks_models.ResultData,
          result=branch_1_result,
          benchmark=benchmark,
          name="load",
          measurement=10)

        G(benchmarks_models.ResultData,
          result=branch_2_result,
          benchmark=benchmark,
          name="load",
          measurement=2)

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

        benchmark = G(benchmarks_models.Benchmark, name="cpu")

        manifest_1 = G(benchmarks_models.Manifest, manifest=MINIMAL_XML)
        manifest_2 = G(benchmarks_models.Manifest, manifest=MINIMAL_XML)

        manifest_1_result = G(benchmarks_models.Result, manifest=manifest_1)

        G(benchmarks_models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",

          measurement=10)

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
