# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Benchmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('displayname', models.CharField(max_length=32)),
                ('display', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='BoardConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Manifest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manifest', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.CharField(max_length=32, null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True)),
                ('gerrit_change_number', models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)),
                ('gerrit_patchset_number', models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)),
                ('gerrit_change_url', models.URLField(null=True, blank=True)),
                ('gerrit_change_id', models.CharField(max_length=42, null=True, blank=True)),
                ('build_url', models.URLField(null=True, blank=True)),
                ('board', models.ForeignKey(related_name='results', to='benchmarks.Board')),
                ('branch', models.ForeignKey(related_name='results', to='benchmarks.Branch')),
                ('configuration', models.ForeignKey(blank=True, to='benchmarks.Configuration', null=True)),
                ('manifest', models.ForeignKey(related_name='results', to='benchmarks.Manifest', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('measurement', models.FloatField()),
                ('timestamp', models.DateTimeField(null=True)),
                ('benchmark', models.ForeignKey(related_name='data', to='benchmarks.Benchmark')),
                ('result', models.ForeignKey(related_name='data', to='benchmarks.Result')),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='configuration',
            field=models.ForeignKey(related_name='boards', to='benchmarks.BoardConfiguration'),
        ),
    ]
