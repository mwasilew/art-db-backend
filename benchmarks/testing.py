from benchmarks.models import Manifest

MINIMAL_XML = '<?xml version="1.0" encoding="UTF-8"?><body></body>'

def MANIFEST():
    m, _ = Manifest.objects.get_or_create(manifest=MINIMAL_XML)
    return m

