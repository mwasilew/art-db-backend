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
