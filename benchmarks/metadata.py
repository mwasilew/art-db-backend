import json
import re


def extract_metadata(definition):
    parser = MetadataParser(definition)
    return parser.metadata

def extract_name(definition):
    parser = MetadataParser(definition)
    return parser.name

def extract_device(definition):
    parser = MetadataParser(definition)
    return parser.device


class MetadataParser(object):

    def __init__(self, definition):
        self.definition = definition
        self.metadata = {}
        self.name = ""
        self.device = None
        self.__extract_metadata_recursively__(self.definition)

    def __extract_metadata_recursively__(self, data):
        if isinstance(data, dict):
            for key in data:
                if key == 'metadata':
                    for k in data[key]:
                        self.metadata[k] = data[key][k]
                elif key == 'job_name':
                    self.name = data[key]
                elif key == 'requested_device_type_id':
                    self.device = data[key]
                elif 'role' in data and 'device_type' in data and data['role'] == 'target':
                    self.device = data['device_type']
                else:
                    self.__extract_metadata_recursively__(data[key])
        elif isinstance(data, list):
            for item in data:
                self.__extract_metadata_recursively__(item)
