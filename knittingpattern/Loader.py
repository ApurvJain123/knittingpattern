import json
import os
import sys


def do_not_process(object):
    return object


class Loader(object):

    def __init__(self, process=do_not_process):
        self.process = process

    def object(self, obj):
        return self.process(obj)

    def string(self, json_string):
        obj = json.loads(json_string)
        return self.object(obj)

    def file(self, file):
        obj = json.load(file)
        return self.object(obj)

    def path(self, path):
        with open(path) as file:
            return self.file(file)

    def url(self, url, encoding="UTF-8"):
        import urllib.request
        with urllib.request.urlopen(url) as file:
            json = file.read()
        json = json.decode(encoding)
        return self.string(json)

    def folder(self, folder):
        result = []
        for root, directories, files in os.walk(folder):
            for file in files:
                path = os.path.join(root, file)
                result.append(self.path(path))
        return result

    def _relative_to_absolute(self, module_location, folder):
        if os.path.isfile(module_location):
            path = os.path.dirname(module_location)
        elif os.path.isdir(module_location):
            path = module_location
        else:
            __import__(module_location)
            module = sys.modules[module_location]
            path = os.path.dirname(module.__file__)
        absolute_path = os.path.join(path, folder)
        return absolute_path

    def relative_folder(self, module, folder):
        folder = self._relative_to_absolute(module, folder)
        return self.folder(folder)

    def relative_file(self, module, file):
        path = self._relative_to_absolute(module, file)
        return self.path(path)

__all__ = ["Loader"]