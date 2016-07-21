import os
from django.core.files import File

def get_file(name):
    return File(open(os.path.join(os.path.dirname(__file__), name)))
