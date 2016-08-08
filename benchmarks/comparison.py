import json
import os
import shutil
import subprocess
import tempfile

from collections import OrderedDict

from django.conf import settings

compare_script = os.getenv('COMPARE_SCRIPT', None)
compare_command = [compare_script]
if not compare_script:
    compare_script = os.path.join(settings.EXTERNAL_DIR['BASE'], 'art-testing',
                                  'compare.py')
    compare_command = [compare_script, '--output-for-linaro-automation']


def render_comparison(testjob_before, testjob_after):
    # FIXME: sandbox this!
    compare_files = [testjob_before.data.file.name,
                     testjob_after.data.file.name]
    output = subprocess.check_output(compare_command + compare_files,
                                     stderr=subprocess.STDOUT)
    return output

def compare(testjob_before, testjob_after):
    result = []
    current_results = testjob_after.result_data.all()
    previous_results = testjob_before.result_data.all()
    for current in current_results:
        __previous__ = [
            r for r in previous_results
            if r.benchmark_id == current.benchmark_id and r.name ==current.name
        ]
        if len(__previous__) == 1:
            previous = __previous__[0]
            change = ((current.measurement / previous.measurement * 100) - 100) * -1
            result.append({
                "current": current,
                "previous": previous,
                "change": change,
            })

    return result
