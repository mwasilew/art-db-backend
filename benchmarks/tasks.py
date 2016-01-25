import os
import json
import urlparse
import subprocess

from django.utils import timezone
from datetime import timedelta

from crayonbox import celery_app
from django.conf import settings
from django.core.files.base import ContentFile
from celery.utils.log import get_task_logger
from benchmarks.models import Benchmark, ResultData, Result

from . import testminer, mail


logger = get_task_logger(__name__)


def _set_testjob_results(testjob):

    netloc = urlparse.urlsplit(testjob.testrunnerurl).netloc
    username, password = settings.CREDENTIALS[netloc]
    tester = getattr(testminer, testjob.testrunnerclass)(testjob.testrunnerurl, username, password)

    testjob.status = tester.get_test_job_status(testjob.id)
    testjob.url = tester.get_job_url(testjob.id)

    if not testjob.initialized:
        testjob.testrunnerclass = tester.get_result_class_name(testjob.id)
        testjob.initialized = True
        testjob.save()
        tester = getattr(testminer, testjob.testrunnerclass)(testjob.testrunnerurl, username, password)

    if testjob.status not in ["Complete", "Incomplete", "Canceled"]:
        testjob.save()
        return

    testjob.definition = tester.get_test_job_details(testjob.id)['definition']
    testjob.completed = True
    test_results = tester.get_test_job_results(testjob.id)

    if not test_results:
        testjob.status = "Results Missing"
        testjob.save()
        return

    datafile_name, datafile_content = tester.get_result_data(testjob.id)
    datafile = ContentFile(datafile_content)

    testjob.data.save(datafile_name, datafile, save=False)
    testjob.save()

    for result in test_results:
        benchmark, _ = Benchmark.objects.get_or_create(
            name=result['benchmark_name']
        )

        for subscore in result['subscore']:
            ResultData.objects.create(
                name=subscore['name'],
                measurement=subscore['measurement'],
                board=result['board'],
                result=testjob.result,
                benchmark=benchmark
            )

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

    logger.info("Fetch benchmark results for %s" % testjob)

    _set_testjob_results(testjob)

    if not testjob.completed:
        logger.info("Testjob for %s not completed, restarting" % testjob)
        set_testjob_results.apply_async(args=[testjob], countdown=300)
    else:
        logger.info("Testjob for %s completed" % testjob)


def _sync_external_repos():
    base = settings.EXTERNAL_DIR['BASE']
    for name, address in settings.EXTERNAL_DIR['REPOSITORIES']:

        logger.info("Repository: %s" % address)

        repo_path = os.path.join(base, name)
        if not os.path.exists(repo_path):
            subprocess.check_call(['git', 'clone', address, repo_path], cwd=base)
        else:
            subprocess.check_call(['git', 'pull'], cwd=repo_path)


@celery_app.task(bind=True)
def sync_external_repos(self):
    _sync_external_repos()


def _weekly_benchmark_progress():

    reports = []

    now = timezone.now() - timedelta(days=7)
    then = now - timedelta(days=1)

    branches = (Result.objects.order_by('branch_name')
                .distinct("branch_name")
                .values_list("branch_name", flat=True))

    for branch_name in branches:
        query = (Result.objects
                 .order_by("-created_at")
                 .filter(gerrit_change_number__isnull=True,
                         branch_name=branch_name))

        current = None
        for item in query.filter(created_at__lte=now, created_at__gte=then):
            if item.data.count():
                current = item
                break

        previous = None
        for item in query.filter(created_at__lte=then, created_at__gte=then):
            if item.data.count():
                previous = item
                break

        import pdb; pdb.set_trace()
        # current = query.filter(created_at__lte=now).first()
        # previous = query.filter(created_at__lte=then).first()

        if current and previous:
            reports.append({
                "branch": branch_name,
                "current": current,
                "previous": previous
            })
        else:
            pass # no items to generate report from

    mail.weekly_benchmark_progress(reports)


@celery_app.task(bind=True)
def weekly_benchmark_progress(self):
    _weekly_benchmark_progress()
