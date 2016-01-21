import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crayonbox.settings.private")

django.setup()

from django.utils.dateparse import parse_datetime
from django.utils import timezone

from benchmarks import models


dump = json.load(open("production.dump.json"))


for manifest in dump['manifests']:
    print models.Manifest.objects.get_or_create(
        manifest_hash=manifest['hash'],
        manifest=manifest['content']
    )


for result in dump['results']:
    manifest = models.Manifest.objects.get(manifest_hash=result['manifest_hash'])

    _result = models.Result.objects.create(
        manifest=manifest,
        name=result['build_url'],
        branch_name=result['branch_name'],

        build_url=result['build_url'],
        build_number=result['build_number'],
        build_id=result['build_id'],

        gerrit_change_number=result['gerrit_change_number'],
        gerrit_patchset_number=result['gerrit_patchset_number'],
        gerrit_change_url=result['gerrit_change_url'],
        gerrit_change_id=result['gerrit_change_id'] or "",

        created_at=timezone.make_aware(parse_datetime(result['created_at']))
    )

    for data in result['data']:
        benchmark, _ = models.Benchmark.objects.get_or_create(name=data['benchmark'])
        _result.data.create(
            benchmark=benchmark,
            name=data['name'],
            board=data['board'],
            measurement=data['measurement'],
            created_at=timezone.make_aware(parse_datetime(data['created_at']))
        )
