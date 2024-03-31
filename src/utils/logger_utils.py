import json


def log_to_json(log):
    return json.dumps(log, indent=4)
