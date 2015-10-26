import hashlib

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from benchmarks import models


class ManifestTests(APITestCase):

    client = APIClient()

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
        models.Manifest.objects.create(manifest=manifest)

        response = self.client.post('/api/manifest/', data={'manifest': manifest})
        self.assertEqual(response.data['manifest_hash'], hashlib.sha1(manifest).hexdigest())
