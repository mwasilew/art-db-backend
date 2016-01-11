import xmlrpclib
import traceback
import urlparse

from crayonbox import celery_app
from celery.utils.log import get_task_logger

from django.conf import settings

from . import models, testminer


logger = get_task_logger(__name__)


def lava_scheduler_job_status(job_id):
    source = "validation.linaro.org"

    credentials = settings.LAVA_CREDENTIALS[source]
    server = xmlrpclib.ServerProxy("http://%s:%s@%s/RPC2" % (
        credentials[0], credentials[1], source))

    try:
        data = server.scheduler.job_status(job_id)
    except xmlrpclib.Error as e:
        logger.error(e.faultString)
        return None

    job_status = data['job_status']
    logger.info("TestJob %s status:%s" % (job_id, job_status))
    return job_status


@celery_app.task
def update_incopleted_testjobs():

    for test_job in models.TestJob.objects.filter(status=None):
        test_job.status = lava_scheduler_job_status(test_job.id)
        test_job.save()


# class TestConfig(object):
#     def __init__(self):
#         self.testrunnerurl = "https://validation.linaro.org/"
#         self.testrunnerclass = "ArtMicrobenchmarksTestResults"


# def get_credentials(netloc):
#     username, password = settings.LAVA_CREDENTIALS[netloc]
#     return (username, password)



# # @celery_app.task
# def dig_test(test_job):

#     tester = TestConfig()
#     test_job_id = test_job
#     # try:
#     test_status = tester.get_test_job_status(test_job_id)
#     print "\tTest job %s: %s (%s)" % (
#         test_job_id,
#         test_status,
#         tester.get_job_url(test_job_id))
#     test_job.status = test_status
#     test_job.save()

#     if tester.test_results_available(test_job_id):
#         test_metadata = tester.get_test_job_details(test_job_id)
#         # metadata contains information about:
#         #  - board
#         test_results = tester.get_test_job_results(test_job_id)

#         # ToDo: not implemented yet. DO NOT REMOVE
#         #for result in test_results['test']:
#         #    name = result['testdef']
#         #    if 'results' in result.keys():
#         #        print "\t\tTest(%s): %s" % (name, result['result'])
#         #    if 'parameters' in result.keys():
#         #        print "\t\t\tParameters: %s" % (result['parameters'])
#         #        print result['parameters'].__class__.__name__
#         #    if 'results' in result.keys() and result['result'] == 'fail':
#         #        print "\t\t\tReason: %s" % (result['reason'])
#         #    version = ''
#         #    if 'version' in result.keys():
#         #        version = result['version']
#         #    parameters = {}
#         #    if 'parameters' in result.keys():
#         #        parameters = result['parameters']

#         tester.cleanup()  # remove all temporary files
#     else:
#         # start a new task after 5 minutes
#         dig_test.apply_async(args=[tester, test_job], countdown=300)
#     return True
#     # except Exception as e:
#     #     print "Exception happened"
#     #     print traceback.print_exc()
#     #     # self.retry(exc=e, countdown=60)


# @celery_app.task(bind=True)
# def download_test_results(self, config, test_job):
#     username, password = get_credentials(
#         urlparse.urlsplit(config.testrunnerurl).netloc
#     )
#     tester = getattr(testminer, config.testrunnerclass)(
#         config.testrunnerurl,
#         username,
#         password,
#         self.request.id
#     )
#     dig_test.delay(tester, test_job)
#     return True
