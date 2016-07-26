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

def render_comparison(testjob_before, testjob_after):
    # FIXME: sandbox this!
    output = subprocess.check_output([
        compare_script,
        testjob_before.data.file.name,
        testjob_after.data.file.name,
    ])
    return output
