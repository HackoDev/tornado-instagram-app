import json


class APIHTTPError(Exception):

    def __init__(self, status_code=500, reason=None):
        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return json.dumps({'detail': self.reason})
