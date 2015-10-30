import hashlib

from django_dynamic_fixture import G
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.test import APITestCase


from benchmarks import models


class ManifestTests(APITestCase):

    def test_get_1(self):
        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_2(self):
        manifest = "content"
        manifest_hash = hashlib.sha1(manifest).hexdigest()

        models.Manifest.objects.create(manifest=manifest)

        response = self.client.get('/api/manifest/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['manifest_hash'], manifest_hash)

    def test_post(self):
        manifest = "content"

        response = self.client.post('/api/manifest/', data={'manifest': manifest})
        self.assertEqual(response.data['manifest_hash'], hashlib.sha1(manifest).hexdigest())
        self.assertEqual(models.Manifest.objects.count(), 1)

        response = self.client.post('/api/manifest/', data={'manifest': manifest})
        self.assertEqual(response.data['manifest_hash'], hashlib.sha1(manifest).hexdigest())
        self.assertEqual(models.Manifest.objects.count(), 1)


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

        manifest_1 = G(models.Manifest, manifest="1")
        manifest_2 = G(models.Manifest, manifest="2")

        manifest_1_result = G(models.Result, manifest=manifest_1)
        manifest_2_result = G(models.Result, manifest=manifest_2)

        G(models.ResultData,
            result=manifest_1_result,
            benchmark=benchmark,
            name="load",

            measurement=10)

        G(models.ResultData,
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

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 10)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], 2)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], 8)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], 0)

    def test_compare_with_manifest_2(self):
        benchmark = G(models.Benchmark, name="cpu")

        manifest_1 = G(models.Manifest, manifest="1")
        manifest_2 = G(models.Manifest, manifest="2")

        manifest_1_result = G(models.Result, manifest=manifest_1)
        manifest_2_result = G(models.Result, manifest=manifest_2)

        G(models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",

          measurement=10)

        G(models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",

          measurement=20)

        G(models.ResultData,
          result=manifest_2_result,
          benchmark=benchmark,
          name="load",

          measurement=2)

        G(models.ResultData,
          result=manifest_2_result,
          benchmark=benchmark,
          name="load",

          measurement=20)

        response = self.client.get('/api/compare/manifest/', {
            'manifest_1': manifest_1.manifest_hash,
            'manifest_2': manifest_2.manifest_hash
        })

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 15)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], 11)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], 4)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 5)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], 9)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], -4)

    def test_compare_with_branch(self):

        benchmark = G(models.Benchmark, name="cpu")

        branch_1 = G(models.Branch)
        branch_2 = G(models.Branch)

        branch_1_result = G(models.Result, branch=branch_1)
        branch_2_result = G(models.Result, branch=branch_2)

        G(models.ResultData,
          result=branch_1_result,
          benchmark=benchmark,
          name="load",

          measurement=10)

        G(models.ResultData,
          result=branch_2_result,
          benchmark=benchmark,
          name="load",

          measurement=2)

        response = self.client.get('/api/compare/branch/', {
            'branch_1': branch_1.name,
            'branch_2': branch_2.name
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

        manifest_1 = G(models.Manifest, manifest="1")
        manifest_2 = G(models.Manifest, manifest="2")

        manifest_1_result = G(models.Result, manifest=manifest_1)

        G(models.ResultData,
          result=manifest_1_result,
          benchmark=benchmark,
          name="load",

          measurement=10)

        response = self.client.get('/api/compare/manifest/', {
            'manifest_1': manifest_1.manifest_hash,
            'manifest_2': manifest_2.manifest_hash
        })

        self.assertEqual(response.data['cpu']['load']['avg']['base'], 10)
        self.assertEqual(response.data['cpu']['load']['avg']['target'], None)
        self.assertEqual(response.data['cpu']['load']['avg']['diff'], None)

        self.assertEqual(response.data['cpu']['load']['stddev']['base'], 0)
        self.assertEqual(response.data['cpu']['load']['stddev']['target'], None)
        self.assertEqual(response.data['cpu']['load']['stddev']['diff'], None)
