import json


# read mapping config
def read_mapping(file_name):
    with open(file_name) as json_data:
        mapped_data = json.load(json_data)
        json_data.close()
        return mapped_data
