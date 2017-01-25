from django.test import TestCase
from mock import patch
import re
import requests

from benchmarks.testminer import GenericLavaTestSystem
from benchmarks.testminer import LavaServerException
from benchmarks.testminer import LavaResponseException
from benchmarks.testminer import ArtMicrobenchmarksTestResults

class MockResponse(object):

    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    @classmethod
    def http_error(__class__, status_code):
        f = lambda method, url, **whatever: __class__(status_code, '')
        return f


class GenericLavaTestSystemTest(TestCase):


    @patch("requests.request", MockResponse.http_error(500))
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


class ArtMicrobenchmarksTestResultsTest(TestCase):

    def test_environment_name_no_metadata(self):
        tester = ArtMicrobenchmarksTestResults('https://example.com/')
        self.assertTrue(tester.get_environment_name({}) is None)

    def test_environment_name_full(self):
        tester = ArtMicrobenchmarksTestResults('https://example.com/')
        metadata = {
            'device': 'nexus9',
            'mode': 64, # an int, on purpose
            'core': 'a57'
        }
        self.assertEqual(tester.get_environment_name(metadata), 'nexus9-64-a57-aot')

    def test_environment_name_with_explicit_compiler_mode(self):
        tester = ArtMicrobenchmarksTestResults('https://example.com/')
        metadata = {
            'device': 'nexus9',
            'mode': 64, # an int, on purpose
            'core': 'a57',
            'compiler-mode': 'jit',
        }
        self.assertEqual(tester.get_environment_name(metadata), 'nexus9-64-a57-jit')

    def test_parse_test_results(self):
        input_json = '{"benchmarks" : { "benchmarks/algorithm/Foo.Bar": [5420897.5, 5434825.5, 5417673.0] } }'
        tester = ArtMicrobenchmarksTestResults('https://example.com/')

        test_result = tester.parse_test_results(input_json)[0]
        self.assertEqual(test_result['benchmark_name'], 'Foo')
        self.assertEqual(test_result['benchmark_group'], 'benchmarks/algorithm/')

        subscore = test_result['subscore'][0]
        self.assertEqual(subscore['name'], 'Bar')
        self.assertEqual(subscore['measurement'], 5420897.5)

    def test_parse_test_results_2(self):
        input_json = '{"benchmarks" : { "benchmarks/group1/Foo.Bar": [5420897.5, 5434825.5, 5417673.0], "benchmarks/group2/Foo.Bar": [5420897.5, 5434825.5, 5417673.0] } }'
        tester = ArtMicrobenchmarksTestResults('https://example.com/')
        test_results = tester.parse_test_results(input_json)
        self.assertEqual(len(test_results), 2)
        self.assertEqual(len([t for t in test_results if t['benchmark_group'] == 'benchmarks/group1/']), 1)
        self.assertEqual(len([t for t in test_results if t['benchmark_group'] == 'benchmarks/group2/']), 1)

    def test_parse_test_results_3(self):
        input_json = '{"benchmarks" : { "benchmarks/group1/Foo.Baz": [420897.5, 434825.5, 417673.0], "benchmarks/group1/FooBar": [5420897.5, 5434825.5, 5417673.0], "benchmarks/group2/Foo.Bar": [5420897.5, 5434825.5, 5417673.0] } }'
        tester = ArtMicrobenchmarksTestResults('https://example.com/')
        test_results = tester.parse_test_results(input_json)
        self.assertEqual(len(test_results), 3)
        self.assertEqual(len([t for t in test_results if t['benchmark_group'] == 'benchmarks/group1/']), 2)
        self.assertEqual(len([t for t in test_results if t['benchmark_group'] == 'benchmarks/group2/']), 1)
