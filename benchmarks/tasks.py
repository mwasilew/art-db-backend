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
    tester = getattr(testminer, testjob.testrunnerclass)(
        testjob.testrunnerurl, username, password
    )

    testjob.status = tester.get_test_job_status(testjob.id)
    testjob.url = tester.get_job_url(testjob.id)

    if not testjob.initialized:
        testjob.testrunnerclass = tester.get_result_class_name(testjob.id)
        testjob.initialized = True
        testjob.save()
        tester = getattr(testminer, testjob.testrunnerclass)(
            testjob.testrunnerurl, username, password
        )

    if testjob.status not in ["Complete", "Incomplete", "Canceled"]:
        logger.debug("Saving job({0}) status: {1}".format(testjob.id, testjob.status))
        testjob.save()
        return

    testjob.definition = tester.get_test_job_details(testjob.id)['definition']
    testjob.completed = True
    logger.debug("Test job({0}) completed: {1}".format(testjob.id, testjob.completed))
    if testjob.status in ["Incomplete", "Canceled"]:
        logger.debug("Saving job({0}) status: {1}".format(testjob.id, testjob.status))
        testjob.save()
        return

    logger.debug("Calling testminer")
    logger.debug("Tester class:{0}".format(tester.__class__.__name__))
    logger.debug("Testjob:{0}".format(testjob.id))
    test_results = tester.get_test_job_results(testjob.id)

    if not test_results and testjob.testrunnerclass != "GenericLavaTestSystem":
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
def update_jenkins(self, result):
    host = urlparse.urlsplit(result.build_url).netloc

    if host not in settings.CREDENTIALS.keys():
        logger.error("No credentials found for %s" % host)
        return

    username, password = settings.CREDENTIALS[host]

    description = render_to_string("jenkins_update.html", {
        "host": settings.URL,
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

    url = result.build_url + "submitDescription"

    response = None

    for _ in range(3):  # retry
        try:
            response = requests.post(url, data=data, headers=headers,
                                     auth=auth, verify=True)

        except requests.exceptions.RequestException:
            continue

        if response.status_code == 200:
            logger.info("Jenkins updated for {0}".format(result))
            return
        if response.status_code == 404:
            logger.warning("Jenkins result not longer available {0}".format(result))
            result.completed = True
            result.reported = True
            result.save()
            return
        logger.warning("Jenkins updated failed, retrying")

    logger.error(u"Jenkins update fail for {0}".format(result))

    if response:
        response.raise_for_status()


@celery_app.task(bind=True)
def check_result_completeness(self):
    for result in models.Result.objects.filter(reported=False):
        if result.completed:
            report_email.apply_async(args=[result])
            report_gerrit.apply_async(args=[result])

            result.reported = True
            result.save()

        update_jenkins.apply_async(args=[result])


@celery_app.task(bind=True)
def report_gerrit(self, current):
    if not current.gerrit_change_id:
        return

    if not current.baseline:
        message = render_to_string("gerrit_update_baseline_missing.html", {
            "current": current,
        })
    elif not current.baseline.data.count():
        message = render_to_string("gerrit_update_baseline_no_results.html", {
            "current": current,
            "baseline": current.baseline
        })
    else:
        results = models.Result.objects.compare(current, current.baseline)

        message = render_to_string("gerrit_update.html", {
            "current": current,
            "baseline": current.baseline,
            "results": results
        })

    gerrit.update(current, message)


@celery_app.task(bind=True)
def report_email(self, current):
    if not current.gerrit_change_id:
        return

    if not current.baseline:
        return mail.result_progress_baseline_missing(current)

    if not current.data.count():
        return mail.result_progress_no_results(current)

    if not current.baseline.data.count():
        return mail.result_progress_baseline_no_results(current)

    results = models.Result.objects.compare(current, current.baseline)
    return mail.result_progress(current, results)


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


@celery_app.task(bind=True)
def daily_benchmark_progress(self):
    now = timezone.now()
    interval = relativedelta(days=1)

    results = models.Result.objects.compare_progress(now, interval)
    if results:
        mail.daily_benchmark_progress(now, interval, results)


@celery_app.task(bind=True)
def weekly_benchmark_progress(self):
    now = timezone.now()
    interval = relativedelta(days=7)

    results = models.Result.objects.compare_progress(now, interval)
    if results:
        mail.weekly_benchmark_progress(now, interval, results)


@celery_app.task(bind=True)
def monthly_benchmark_progress(self):
    now = timezone.now()
    interval = relativedelta(months=1)

    results = models.Result.objects.compare_progress(now, interval)
    if results:
        mail.monthly_benchmark_progress(now, interval, results)
