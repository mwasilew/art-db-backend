import xmlrpclib
import traceback
import urlparse

from benchmarks.models import (
    Benchmark,
    Board,
    ResultData
)
from crayonbox import celery_app
from celery.utils.log import get_task_logger

from django.conf import settings

from . import testminer


logger = get_task_logger(__name__)


class TestConfig(object):
    def __init__(self):
        self.testrunnerurl = "https://validation.linaro.org/"
        self.testrunnerclass = "ArtMicrobenchmarksTestResults"


def get_credentials(netloc):
    username, password = settings.CREDENTIALS[netloc]
    return (username, password)



@celery_app.task(bind=True)
def dig_test(self, tester, test_job):

    test_job_id = test_job.id
    # try:
    test_status = tester.get_test_job_status(test_job_id)
    logger.info( "\tTest job %s: %s (%s)" % (
        test_job_id,
        test_status,
        tester.get_job_url(test_job_id)))
    test_job.status = test_status
    test_job.save()

    if tester.test_results_available(test_job_id):
        test_metadata = tester.get_test_job_details(test_job_id)
        test_job.definition = test_metadata['definition']
        test_job.url = tester.get_job_url(test_job_id)
        test_job.save()

        test_results = tester.get_test_job_results(test_job_id)
        if not test_results:
            test_job.status = "Results Missing"
            test_job.save()
        for benchmark in test_results:
            # {'subscore': [{'name': u'LongRotateLeft_32', 'measurement': 812.58}, {'name': u'IntegerRotateRight_32', 'measurement': 115.13}, {'name': u'IntegerRotateLeft_32', 'measurement': 116.78}, {'name': u'LongRotateRight_32', 'measurement': 813.57}, {'name': u'SHA1DigestProcessBlock_32', 'measurement': 768.09}], 'board_config': u'mn-nexus9-02', 'board': u'mn-nexus9-02', 'benchmark_name': u'BitfieldRotate'}
            db_board, created = Board.objects.get_or_create(
                displayname=benchmark['board'],
                display=benchmark['board']
            )
            db_benchmark, created = Benchmark.objects.get_or_create(
                name=benchmark['benchmark_name']
            )

            test_job.result.board = db_board
            test_job.result.save()

            for subscore in benchmark['subscore']:
                db_resultdata = ResultData(
                    name=subscore['name'],
                    measurement=subscore['measurement'],
                    result=test_job.result,
                    benchmark=db_benchmark
                )
                db_resultdata.save()



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

        tester.cleanup()  # remove all temporary files
    else:
        # start a new task after 5 minutes
        dig_test.apply_async(args=[tester, test_job], countdown=300)
    return True
    # except Exception as e:
    #     print "Exception happened"
    #     print traceback.print_exc()
    #     # self.retry(exc=e, countdown=60)


@celery_app.task(bind=True)
def download_test_results(self, config, test_job):
    username, password = get_credentials(
        urlparse.urlsplit(config.testrunnerurl).netloc
    )
    tester = getattr(testminer, config.testrunnerclass)(
        config.testrunnerurl,
        username,
        password,
        self.request.id
    )
    dig_test.delay(tester, test_job)
    return True
