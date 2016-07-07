from django.core.exceptions import ValidationError
from django.test import TestCase

from benchmarks.models import BenchmarkGroup

class BenchmarkGroupProgressTest(TestCase):

    def test_name_must_be_unique(self):
        BenchmarkGroup.objects.create(name='bar/')
        with self.assertRaises(ValidationError):
            BenchmarkGroup.objects.create(name='bar/')


