import json
import urlparse

from crayonbox import celery_app
from benchmarks.models import Benchmark, ResultData

from django.conf import settings

from . import testminer


class TestConfig(object):
    def __init__(self):
        self.testrunnerurl = "https://validation.linaro.org/"
        self.testrunnerclass = "ArtMicrobenchmarksTestResults"


def _set_testjob_results(testjob):

    config = TestConfig()
    netloc = urlparse.urlsplit(config.testrunnerurl).netloc
    username, password = settings.CREDENTIALS[netloc]
    tester = getattr(testminer, config.testrunnerclass)(config.testrunnerurl, username, password)

    testjob.status = tester.get_test_job_status(testjob.id)
    testjob.url = tester.get_job_url(testjob.id)

    if not tester.test_results_available(testjob.id):
        testjob.save()
        return

    test_results = tester.get_test_job_results(testjob.id)

    if not test_results:
        testjob.status = "Results Missing"
        testjob.completed = True
        testjob.save()
        return

    ResultData.objects.filter(testjob=testjob).delete()

    for result in test_results:
        benchmark, _ = Benchmark.objects.get_or_create(
            name=result['benchmark_name']
        )

        for subscore in result['subscore']:
            ResultData.objects.create(
                name=subscore['name'],
                measurement=subscore['measurement'],
                board=result['board'],
                testjob=testjob,
                benchmark=benchmark
            )

    testjob.definition = tester.get_test_job_details(testjob.id)['definition']
    testjob.completed = True
    testjob.save()

    tester.cleanup()

    # ToDo: not implemented yet. DO NOT REMOVE
    #for result in test_results['test']:
    #    name = result['testdef']
    #    if 'results' in result.keys():
    #        print "\t\tTest(%s): %s" % (name, result['result'])
    #    if 'parameters' in result.keys():
    #        print "\t\t\tParameters: %s" % (result['parameters'])
    #        print result['parameters'].__class__.__name__
    #    if 'results' in result.keys() and result['result'] == 'fail':
    #        print "\t\t\tReason: %s" % (result['reason'])
    #    version = ''
    #    if 'version' in result.keys():
    #        version = result['version']
    #    parameters = {}
    #    if 'parameters' in result.keys():
    #        parameters = result['parameters']


@celery_app.task(bind=True)
def set_testjob_results(self, testjob):

    _set_testjob_results(testjob)

    if not testjob.completed:
        set_testjob_results.apply_async(args=[testjob], countdown=300)
