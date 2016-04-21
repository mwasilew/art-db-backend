import json


def extract_metadata(definition):
    parser = MetadataParser(definition)
    parser.parse()
    return parser.metadata

def extract_name(definition):
    parser = MetadataParser(definition)
    parser.parse()
    return parser.name


class MetadataParser(object):

    def __init__(self, definition):
        self.definition = definition
        self.metadata = {}
        self.name = ""

    def parse(self):
        if self.definition:
            possible_loaders = [
                json.loads,
            ]
            for loader in possible_loaders:
                try:
                    data = loader(self.definition)
                    self.metadata = {}
                    self.__extract_metadata_recursively__(data)
                    return
                except ValueError:
                    pass

    def __extract_metadata_recursively__(self, data):
        if type(data) is dict:
            for key in data:
                if key == 'metadata':
                    for k in data[key]:
                        self.metadata[k] = data[key][k]
                elif key == 'job_name':
                    self.name = data[key]
                else:
                    self.__extract_metadata_recursively__(data[key])
        elif type(data) is list:
            for item in data:
                self.__extract_metadata_recursively__(item)
