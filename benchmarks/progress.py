# encoding=UTF-8

from benchmarks.models import Environment, Result, TestJob


class Progress(object):
    def __init__(self, project, branch, environment, before, after):
        self.project = project
        self.branch = branch
        self.environment = environment
        self.before = before
        self.after = after

    def __str__(self):
        return '<%s %s %s; %s -> %s>' % (
            self.project,
            self.branch,
            self.environment.identifier,
            self.before.created_at,
            self.after.created_at,
        )
    def __unicode__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()

def get_values(queryset, field):
    data = queryset.distinct(field).order_by(field).values(field)
    return [item[field] for item in data]


def get_progress_since(date):
    result = []

    builds = Result.objects.filter(gerrit_change_number=None)  # only baseline
    projects = get_values(builds, 'name')
    branches = get_values(builds, 'branch_name')
    environments = Environment.objects.all()

    for project in projects:
        for branch in branches:
            for environment in environments:
                testjobs = TestJob.objects.filter(
                    environment=environment,
                    result__branch_name=branch,
                    result__name=project,
                ).order_by('created_at')

                after = testjobs.filter(created_at__gt=date).last()

                if after is None:
                    continue

                before = testjobs.filter(created_at__lte=date).last()

                if before is None:
                    continue

                progress = Progress(
                    project=project,
                    branch=branch,
                    environment=environment,
                    before=before,
                    after=after,
                )

                result.append(progress)

    return result


def get_progress_between_results(current, baseline):
    result = []

    for current_testjob in current.test_jobs.all():

        environment = current_testjob.environment
        baseline_testjob = baseline.test_jobs.get(environment=environment)

        if baseline_testjob:
            progress = Progress(
                project=current.name,
                branch=current.branch_name,
                environment=environment,
                before=baseline_testjob,
                after=current_testjob,
            )
            result.append(progress)

    return result
