import json
import os
import shutil
import subprocess
import tempfile

from collections import OrderedDict

from django.conf import settings

compare_script = os.getenv('COMPARE_SCRIPT', None)
if not compare_script:
    compare_script = os.path.join(settings.EXTERNAL_DIR['BASE'], 'art-testing', 'compare.py')

def render_comparison(results_before, results_after):
    tmpdir = export_data(results_before, results_after)
    # FIXME: sandbox this!
    output = subprocess.check_output([
        compare_script,
        os.path.join(tmpdir, "before.json"),
        os.path.join(tmpdir, "after.json"),
    ])
    shutil.rmtree(tmpdir)
    return output


def export_data(results_before, results_after):
    tmpdir = tempfile.mkdtemp()

    export_result(results_before, os.path.join(tmpdir, 'before.json'))
    export_result(results_after, os.path.join(tmpdir, 'after.json'))

    return tmpdir


def export_result(results, filename):
    benchmarks = OrderedDict()
    for benchmark in results.order_by("name"):
        benchmarks[benchmark.name] = benchmark.values

    with open(filename, 'w') as export:
        export.write(json.dumps({"benchmarks": benchmarks}))

