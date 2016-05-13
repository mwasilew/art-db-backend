import json
import os
import shutil
import subprocess
import tempfile

from django.conf import settings

compare_script = os.path.join(os.path.dirname(__file__), '../ext/art-testing/compare.py')

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
    benchmarks = {}
    for benchmark in results:
        benchmarks[benchmark.name] = benchmark.values

    with open(filename, 'w') as export:
        export.write(json.dumps({"benchmarks": benchmarks}))

