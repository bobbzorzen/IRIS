import os
import json


def open_file_as_string(filepath):
    with open(filepath, 'r') as ftemp:
        templateString = ftemp.read()
    return templateString


def fetch_json_file_as_dict(path_to_json):
    json_str = open_file_as_string(path_to_json)
    return json_string_to_dict(json_str)


def json_string_to_dict(json_string):
    json_dict = json.loads(json_string)
    return json_dict
