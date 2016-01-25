from django.template.loader import get_template
from django.core.mail import send_mail
from django.utils import timezone


def weekly_benchmark_progress(reports):

    header = "Art - Weekly Benchmark Progress"
    time = timezone.now().strftime('Week %W %Y')

    results_by_branch = []

    for item in reports:

        measurement_previous =  {d.name: d.measurement for d in item['previous'].data.all()}
        results = []

        for benchmark_result in item['current'].data.order_by("name"):
            current_value = benchmark_result.measurement
            previous_value = measurement_previous.get(benchmark_result.name)
            change = previous_value / current_value if previous_value else None

            results.append({
                "benchmark": benchmark_result.benchmark.name,
                "name": benchmark_result.name,
                "current_value": current_value,
                "previous_value": previous_value,
                "change": change
            })

        results_by_branch.append({"branch": item['branch'], "results": results})

    context = {
        "header": header,
        "time": time,
        "results": results_by_branch,
    }

    template = get_template('weekly_benchmark_progress.html')
    message = template.render(context)

    subject = "%s [%s]" % (header, time)

    from_email = "sebastian.pawlus@linaro.org"
    to_email = ["sebastian.pawlus@gmail.com"]

    send_mail(subject,
              None,
              from_email,
              to_email,
              html_message=message)
