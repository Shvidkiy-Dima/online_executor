import io
import sys
import json

class Response:
    type = 'json'
    body = ''
    status_code = 200

    def __init__(self):
        self.stdout = sys.stdout

    def lock(self):
        sys.stdout = io.StringIO()

    def print_result(self):
        sys.stdout = self.stdout
        body = self.body
        if self.type == 'json':
            try:
                body = json.dumps(body or {})
            except Exception:
                body = json.dumps({'error': 'not json serializable'})
                self.status_code = 400

        data = json.dumps({'type': self.type, 'body': body, 'status_code': self.status_code})
        sys.stdout.write(data)


response = Response()