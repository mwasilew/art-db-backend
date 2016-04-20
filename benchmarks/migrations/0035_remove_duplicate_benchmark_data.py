# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models, connection


def get_benchmark_names(result):
    cursor = connection.cursor()
    cursor.execute("SELECT distinct name from benchmarks_resultdata WHERE result_id = %d" % result.id)
    return [row[0] for row in cursor.fetchall()]


def remove_duplicated_benchmark_data(apps, schema_editor):
    Benchmark = apps.get_model('benchmarks', 'Benchmark')
    Result = apps.get_model('benchmarks', 'Result')
    ResultData = apps.get_model('benchmarks', 'ResultData')
    for result in Result.objects.all():
        for name in get_benchmark_names(result):
            first = ResultData.objects.filter(result=result, name=name).order_by('created_at').first()
            extra = ResultData.objects.filter(result=result, name=name, created_at__gt=first.created_at)
            extra.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0034_populate_testjob_metadata'),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicated_benchmark_data,
            reverse_code=migrations.RunPython.noop,
        )
    ]
