from django.test import TestCase
from mock import patch
import re
import requests

from benchmarks.testminer import GenericLavaTestSystem
from benchmarks.testminer import LavaServerException
from benchmarks.testminer import LavaResponseException

class MockResponse(object):

    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    @classmethod
    def promise(__class__, status_code):
        f = lambda method, url, **whatever: __class__(500, '')
        return f


class GenericLavaTestSystemTest(TestCase):


    @patch("requests.request", MockResponse.promise(500))
    def test_lava_server_request_handling(self):
        tester = GenericLavaTestSystem('http://example.com/')
        with self.assertRaises(LavaServerException):
            tester.get_test_job_status(9999)


class LavaServerExceptionTest(TestCase):

    def test_status_code(self):
        ex = LavaServerException('http://example.com/', 200)
        self.assertEqual(200, ex.status_code)

    def test_status_code_as_string(self):
        ex = LavaServerException('http://example.com/', "404")
        self.assertEqual(404, ex.status_code)

    def test_includes_hostname_and_status_code_in_error_message(self):
        ex = LavaServerException('http://example.com/', 500)
        self.assertTrue(re.match('http://example.com.*500', ex.message) is not None)


class LavaResponseExceptionTest(TestCase):

    def test_message(self):
        ex = LavaResponseException("foo is FUBAR")
        self.assertEqual("foo is FUBAR", ex.message)
