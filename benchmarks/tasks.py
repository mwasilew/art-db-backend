import os
import urlparse
import requests
import subprocess

from dateutil.relativedelta import relativedelta
from urllib import urlencode

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from celery.utils.log import get_task_logger

from crayonbox import celery_app

from . import models, testminer, mail, gerrit

logger = get_task_logger("tasks")


@celery_app.task(bind=True)
def set_testjob_results(self, testjob):

    logger.info("Fetch benchmark results for %s" % testjob)

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
    if testjob.status in ["Incomplete", "Canceled"]:
        testjob.save()

        update_jenkins.delay(testjob.result)
        return

    test_results = tester.get_test_job_results(testjob.id)

    if not test_results:
        testjob.status = "Results Missing"
        testjob.save()
        return

    datafile_name, datafile_content = tester.get_result_data(testjob.id)

    if datafile_name and datafile_content:
        datafile = ContentFile(datafile_content)
        testjob.data.save(datafile_name, datafile, save=False)

    testjob.save()

    for result in test_results:
        benchmark, _ = models.Benchmark.objects.get_or_create(
            name=result['benchmark_name']
        )

        subscore_results = {}
        for item in result['subscore']:
            if item['name'] in subscore_results:
                subscore_results[item['name']].append(item['measurement'])
            else:
                subscore_results[item['name']] = [item['measurement']]

        for name, values in subscore_results.items():
            models.ResultData.objects.create(
                name=name,
                values=values,
                board=result['board'],
                result=testjob.result,
                benchmark=benchmark
            )

    testjob.save()
    tester.cleanup()

    update_jenkins.delay(testjob.result)

    # ToDo: not implemented yet. DO NOT REMOVE
    # for result in test_results['test']:
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
def check_testjob_completeness(self):
    incompleted = models.TestJob.objects.filter(completed=False)

    logger.info("Fetch incomplete TestJobs results, count=%s" % incompleted.count())

    for testjob in models.TestJob.objects.filter(completed=False):
        set_testjob_results.apply_async(args=[testjob])


@celery_app.task(bind=True)
def report_gerrit(self, result):

    other = result.to_compare()
    if not other:
        return

    results = models.Result.objects.compare(result, other)

    message = render_to_string("gerrit_update.html", {
        "current": result,
        "previous": other,
        "results": results
    })

    gerrit.update(result, message)


@celery_app.task(bind=True)
def update_jenkins(self, result):

    host = urlparse.urlsplit(result.build_url).netloc

    if host not in settings.CREDENTIALS.keys():
        logger.error("No credentials found for %s" % host)
        return

    username, password = settings.CREDENTIALS[host]

    description = render_to_string("jenkins_update.html", {
        "host": settings.HOST,
        "result": result,
        "testjobs": models.TestJob.objects.filter(result=result)
    })

    auth = requests.auth.HTTPBasicAuth(username, password)

    crumb_url = ("https://{0}/jenkins/crumbIssuer/api/xml"
                 "?xpath=concat(//crumbRequestField,%22:%22,//crumb)".format(host))

    crumb_response = requests.get(crumb_url, auth=auth)

    if crumb_response.status_code != 200:
        logger.error("crumb retrieval failed with status {0}".format(crumb_response.status_code))
        logger.error(crumb_response.text)
        return

    crumb = crumb_response.text
    logger.info("crumb received")

    data = urlencode({'description': description, "crumb": crumb.split(":")[1]})

    headers = {
        crumb.split(":")[0]: crumb.split(":")[1],
        "Content-Length": len(data),
        "Content-Type": "application/x-www-form-urlencoded"
    }

    url = result.build_url + "/submitDescription"

    response = requests.post(url, data=data, headers=headers, auth=auth, verify=True)

    if response.status_code == 200:
        logger.info("Jenkins updated for {0}".format(result))
    else:
        logger.error(u"Jenkins update fail for {0}: {1}".format(result, response.text))


@celery_app.task(bind=True)
def check_result_completeness(self):
    for result in models.Result.objects.filter(completed=True, reported=False):

        report_email.apply_async(args=[result])
        report_gerrit.apply_async(args=[result])

        result.reported = True
        result.save()


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
def report_email(self, result):
    other = result.to_compare()
    if not other:
        return

    results = models.Result.objects.compare(result, other)

    mail.current_benchmark_progress(result, other, results)


@celery_app.task(bind=True)
def sync_external_repos(self):
    _sync_external_repos()


@celery_app.task(bind=True)
def weekly_benchmark_progress(self):
    now = timezone.now()
    then = relativedelta(days=7)

    results = _benchmark_progress(now, then)

    mail.weekly_benchmark_progress(now, then, results)


@celery_app.task(bind=True)
def monthly_benchmark_progress(self):

    now = timezone.now()
    then = relativedelta(months=1)
    results = _benchmark_progress(now, then)

    mail.monthly_benchmark_progress(now, then, results)


def _benchmark_progress(now, interval):
    return models.Result.objects.compare_progress(now, interval)
