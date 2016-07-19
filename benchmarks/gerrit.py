import logging
import urlparse
import requests
import subprocess

from django.conf import settings


logger = logging.getLogger("tasks")


def http(result, message):
    host = urlparse.urlsplit(result.gerrit_change_url).netloc

    url = "https://%s/a/changes/%s/revisions/%s/review" % (
        host,
        result.gerrit_change_number,
        result.gerrit_patchset_number
    )

    data = {
        'message': message,
        'labels': {'Code-Review': ' 0'}
    }

    username, password = settings.CREDENTIALS[host]

    auth = requests.auth.HTTPDigestAuth(username, password)
    response = requests.post(url, json=data, auth=auth, verify=True)
    response.raise_for_status()


def ssh(result, message):
    host = urlparse.urlsplit(result.gerrit_change_url).netloc

    change_number = result.gerrit_change_number
    patchset_number = result.gerrit_patchset_number

    username, password = settings.CREDENTIALS[host]

    subprocess.check_call(
        ['ssh', '-i', password, '-p', '29418',
         '-o', 'UserKnownHostsFile=/dev/null',
         '-o', 'StrictHostKeyChecking=no',
         '%s@%s' % (username, host),
         'gerrit', 'review', '-m', '"%s"' % message,
         '--code-review', ' 0', '%s,%s' % (change_number, patchset_number)],
        stderr=subprocess.STDOUT)

methods = {
    "android-review.linaro.org": http,
    "review.linaro.org": http,
    "dev-private-review.linaro.org": ssh
}


def update(result, message):
    host = urlparse.urlsplit(result.gerrit_change_url).netloc

    method = methods[host]
    try:
        method(result, message)
        logger.info("Gerrit update for %s, method: '%s'" % (result, method.__name__))
    except:
        logger.exception("Gerrit update failed")
