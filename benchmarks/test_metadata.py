from django.test import TestCase


from benchmarks.metadata import extract_metadata
from benchmarks.metadata import extract_name
from benchmarks.metadata import extract_device


class MetadataParserTestCase(TestCase):

    def test_invalid_json(self):
        self.assertEqual({}, extract_metadata('//'))

    def test_extract_metadata_from_empty_definition(self):
        self.assertEqual({}, extract_metadata(None))

    def test_extract_metadata_from_json_definition(self):
        metadata = extract_metadata({ "metadata" : { "foo": "bar", "baz": "qux" } })

        self.assertEqual(metadata['foo'], 'bar')
        self.assertEqual(metadata['baz'], 'qux')

    def test_extract_metadata_from_nested_metadata(self):
        metadata = extract_metadata({ "something": { "name": "foobar", "metadata" : { "foo": "bar", "baz": "qux" } } })

        self.assertEqual(metadata['foo'], 'bar')
        self.assertEqual(metadata['baz'], 'qux')

    def test_extract_metadata_from_lava_job(self):
        metadata = extract_metadata({"actions": [{"command": "dummy_deploy", "metadata": {"foo": "bar"}}]})
        self.assertEqual(metadata['foo'], 'bar')

    def test_extract_metadata_from_lava_job_with_multiple_actions(self):
        metadata = extract_metadata({"actions": [{"command": "dummy_deploy", "metadata": {"foo": "bar"}}, {"command": "dummy_deploy", "metadata": {"baz": "qux"}}]})
        self.assertEqual(metadata['foo'], 'bar')
        self.assertEqual(metadata['baz'], 'qux')

    def test_extract_name_simple(self):
        name = extract_name({"job_name": "foobar"})
        self.assertEqual(name, 'foobar')

    def test_extract_device(self):
        device = extract_device({"requested_device_type_id": "mydevice"})
        self.assertEqual(device, "mydevice")

    def test_extract_device_from_multinode_job(self):
        device = extract_device({ "device_group": [ { "role": "host", "device_type": "foo" }, { "role": "target", "device_type": "bar"} ]})
        self.assertEqual(device, "bar")

    def test_extract_device_from_multinode_job_without_mn_prefix(self):
        device = extract_device({ "device_group": [ { "role": "host", "device_type": "foo" }, { "role": "target", "device_type": "mn-nexus5x"} ]})
        self.assertEqual(device, "nexus5x")
