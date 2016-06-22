from django.test import TestCase
from django.db.utils import IntegrityError

from benchmarks.models import Environment

class EnvironmentTest(TestCase):

    def test_identifier_is_unique(self):
        Environment(identifier='foo').save()
        with self.assertRaises(IntegrityError):
            Environment(identifier='foo').save()

    def test_use_identifier_as_name_by_default(self):
        e = Environment(identifier='foo')
        e.save()
        self.assertEquals(e.name, 'foo')
