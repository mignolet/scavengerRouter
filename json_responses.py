import json
import sys


def json_data(data, response_code=200):
    return json.dumps(data), response_code, {'Content-Type': 'application/json'}


def json_response(text, response_code=200):
    return json_data({'message': text}, response_code)


def json_error(text, response_code=400):
    sys.stderr.write('[JSON_ERROR, HTTP %d] => %s\n' % (response_code, text))
    return json_response(text, response_code)
