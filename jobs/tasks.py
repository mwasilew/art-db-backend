from crayonbox import celery_app
from celery.utils.log import get_task_logger

from . import models

@celery_app.task
def check_incomplete_testjob():

    print models.TestJob.objects.all()
    print models.BuildJob.objects.all()

    return 2
