from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from benchmarks import progress
from benchmarks.comparison import render_comparison


def result_progress(current, baseline):
    results = progress.get_progress_betwewn_results(current, baseline)
    _send_results(
        current=current,
        template='result_progress.html',
        comparison={p: render_comparison(p.before, p.after) for p in results},
        baseline=current.baseline,
        header="Art - Benchmark Progress for %s" % current.name,
        subject_template="%s [%s]",
    )

def result_progress_baseline_missing(current):
    _send_results(
        current=current,
        template='result_progress_baseline_missing.html',
        header="Art - Benchmark Progress for %s" % current.name,
        subject_template='%s, missing baseline - %s',
    )


def result_progress_baseline_no_results(current):
    _send_results(
        current=current,
        baseline=current.baseline,
        template='result_progress_baseline_no_results.html',
        header="Art - Benchmark Progress for %s" % current.name,
        subject_template='%s, baseline missing results - %s',
    )


def result_progress_no_results(current):
    _send_results(
        current=current,
        baseline=current.baseline,
        template='result_progress_no_results.html',
        header="Art - Benchmark Progress for %s" % current.name,
        subject_template="%s, missing results - %s"
    )


def _send_results(current, template, header, subject_template, comparison=None, baseline=None):
    time = current.created_at.strftime("%d-%m-%Y %H:%M:%S")

    context = {
        "header": header,
        "time": time,
        "comparison": comparison,
        "current": current,
        "baseline": baseline,
    }

    message = render_to_string(template, context)

    subject = subject_template % (header, time)

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


def daily_benchmark_progress(now, then, results):
    header = "Art - Daily Benchmark Progress"
    time = now.strftime('%d %m %Y')

    comparisons = {p: render_comparison(p.before, p.after) for p in results}

    context = {
        "now": now,
        "header": header,
        "time": time,
        "comparisons": comparisons,
    }

    _benchmark_progress(context)


def monthly_benchmark_progress(now, then, results):
    header = "Art - Monthly Benchmark Progress"
    time = now.strftime('%B %Y')
    comparisons = {p: render_comparison(p.before, p.after) for p in results}

    context = {
        "now": now,
        "header": header,
        "time": time,
        "comparisons": comparisons,
    }

    _benchmark_progress(context)


def weekly_benchmark_progress(now, then, results):
    header = "Art - Weekly Benchmark Progress"
    time = now.strftime('Week %W %Y')

    comparisons = {p: render_comparison(p.before, p.after) for p in results}

    context = {
        "now": now,
        "header": header,
        "time": time,
        "comparisons": comparisons,
    }

    _benchmark_progress(context)
