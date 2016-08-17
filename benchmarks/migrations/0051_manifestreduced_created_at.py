# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


INIT_MANIFESTREDUCED_CREATED_AT = """
UPDATE benchmarks_manifestreduced
SET created_at = (
  SELECT min(created_at)
  FROM benchmarks_result
  JOIN benchmarks_manifest ON benchmarks_manifest.id = benchmarks_result.manifest_id
  WHERE benchmarks_manifest.reduced_id = benchmarks_manifestreduced.hash
)
"""

class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0050_benchmarkgroupsummary'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manifestreduced',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='manifestreduced',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.RunSQL(
          sql=INIT_MANIFESTREDUCED_CREATED_AT,
          reverse_sql='SELECT 1',  # i.e. nothing
        )
    ]
