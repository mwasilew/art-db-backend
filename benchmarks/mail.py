from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string


def result_progress(current, results):
    time = current.created_at

    header = "Art - Benchmark Progress for %s" % current.name

    context = {
        "header": header,
        "time": time,
        "results": results,
        "current": current,
        "baseline": current.baseline
    }

    message = render_to_string('result_progress.html', context)

    subject = "%s [%s]" % (context['header'], context['time'])

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.EMAIL_REPORTS_TO

    send_mail(subject, None, from_email, to_email, html_message=message)


def result_progress_baseline_missing(current):
    time = current.created_at.strftime("%d-%m-%Y %H:%M:%S")

    header = "Art - Benchmark Progress for %s" % current.name

    context = {
        "header": header,
        "time": time,
        "current": current,
    }

    message = render_to_string('result_progress_baseline_missing.html', context)

    subject = "%s, missing baseline - %s" % (context['header'], context['time'])

    attachments = [("manifest.xml", current.manifest.manifest, "application/xml")]

    email = EmailMessage(subject,
                         message,
                         settings.DEFAULT_FROM_EMAIL,
                         settings.EMAIL_REPORTS_TO,
                         attachments=attachments)

    email.content_subtype = "html"
    email.send()


def result_progress_baseline_no_results(current):
    time = current.created_at.strftime("%d-%m-%Y %H:%M:%S")

    header = "Art - Benchmark Progress for %s" % current.name

    context = {
        "header": header,
        "time": time,
        "current": current,
        "baseline": current.baseline,
    }

    message = render_to_string('result_progress_baseline_no_results.html', context)

    subject = "%s, missing baseline results - %s" % (context['header'], context['time'])

    attachments = [("manifest.xml", current.manifest.manifest, "application/xml")]

    email = EmailMessage(subject,
                         message,
                         settings.DEFAULT_FROM_EMAIL,
                         settings.EMAIL_REPORTS_TO,
                         attachments=attachments)

    email.content_subtype = "html"
    email.send()


def _benchmark_progress(context):
    message = render_to_string('benchmark_progress.html', context)

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

    _benchmark_progress(context)


def weekly_benchmark_progress(now, then, results):
    header = "Art - Weekly Benchmark Progress"
    time = now.strftime('Week %W %Y')

    context = {
        "now": now,
        "header": header,
        "time": time,
        "results": results
    }

    _benchmark_progress(context)
