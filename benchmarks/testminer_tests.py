from django.test import TestCase

from benchmarks.testminer import LavaServerException
from benchmarks.testminer import LavaResponseException

class LavaServerExceptionTest(TestCase):

    def test_status_code(self):
        ex = LavaServerException(200)
        self.assertEqual(200, ex.status_code)

    def test_status_code_as_string(self):
        ex = LavaServerException("404")
        self.assertEqual(404, ex.status_code)


class LavaResponseExceptionTest(TestCase):

    def test_message(self):
        ex = LavaResponseException("foo is FUBAR")
        self.assertEqual("foo is FUBAR", ex.message)
