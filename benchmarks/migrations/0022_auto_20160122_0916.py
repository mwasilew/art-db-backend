# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def mean(data):
    n = len(data)
    if n < 1:
        return 0
    return sum(data)/float(n)


def migrate(apps, schema_editor):
    Model = apps.get_model("benchmarks", "Result")

    restuls_ret_val = {}

    for result in Model.objects.all():

        ret_val = {}

        for item in result.data.all():

            name = item.name

            if item.name in ret_val:
                ret_val[name]["values"].append(item.measurement)
            else:
                ret_val[name] = {
                    "result": item.result,
                    "name": item.name,
                    "benchmark": item.benchmark,
                    "board": item.board,
                    "created_at": item.created_at,
                    "values": [item.measurement]
                }

        restuls_ret_val[result.id] = ret_val.values()


    ResultData = apps.get_model("benchmarks", "ResultData")

    ResultData.objects.all().delete()

    for pk, value in restuls_ret_val.items():
        for item in value:
            result = ResultData.objects.create(
                benchmark=item['benchmark'],
                board=item['board'],
                name=item['name'],
                result=item['result'],
                values=item['values'],
                created_at=item['created_at'],

                measurement=mean(item['values'])
            )

class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0021_resultdata_values'),
    ]

    operations = [
        migrations.RunPython(migrate, migrations.RunPython.noop),
    ]
