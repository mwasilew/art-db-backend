from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def benchmark_progress(context):
    message = render_to_string('benchmark_progress.html', context)

    subject = "%s [%s]" % (context['header'], context['time'])

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.EMAIL_REPORTS_TO

    send_mail(subject, None, from_email, to_email, html_message=message)


def current_benchmark_progress(current, previous, results):
    header = "Art - Monthly Benchmark Progress"
    time = current.created_at

    header = "Art - Benchmark Progress for %s" % current.name

    context = {
        "header": header,
        "time": time,
        "results": results,
        "current": current,
        "previous": previous
    }

    message = render_to_string('benchmark_report.html', context)

    subject = "%s [%s]" % (context['header'], context['time'])

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.EMAIL_REPORTS_TO

    send_mail(subject, None, from_email, to_email, html_message=message)


def monthly_benchmark_progress(now, then, results):
    header = "Art - Monthly Benchmark Progress"
    time = now.strftime('%B %Y')

    context = {
        "now": now,
        "header": header,
        "time": time,
        "results": results
    }

    benchmark_progress(context)


def weekly_benchmark_progress(now, then, results):
    header = "Art - Weekly Benchmark Progress"
    time = now.strftime('Week %W %Y')

    context = {
        "now": now,
        "header": header,
        "time": time,
        "results": results
    }

    benchmark_progress(context)
