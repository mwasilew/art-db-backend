from django.test import TestCase
from subprocess import check_call

class TestCodeQuality(TestCase):

    def test_flake8(self):
        check_call(['flake8', '--select=F821,F823', '.', '--exclude=.svn,CVS,.bzr,.hg,.git,__pycache__,.tox,.virtualenv,ext'])


