from base64 import b64encode
from werkzeug.exceptions import HTTPException
import json


class TestClient():
    def __init__(self, app, username, password):
        self.app = app
        self.auth = 'Basic ' + b64encode((username + ':' + password)
                                         .encode('utf-8')).decode('utf-8')

    def send(self, url, method='GET', data=None, headers={}):
        headers = headers.copy()
        headers['Authorization'] = self.auth
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        if data:
            data = json.dumps(data)

        with self.app.test_request_context(url, method=method, data=data,
                                           headers=headers):
            try:
                rv = self.app.preprocess_request()
                if rv is None:
                    rv = self.app.dispatch_request()
                rv = self.app.make_response(rv)
                rv = self.app.process_response(rv)
            except HTTPException as e:
                rv = self.app.handle_user_exception(e)

        return rv, json.loads(rv.data.decode('utf-8'))

    def get(self, url, headers={}):
        return self.send(url, 'GET', headers=headers)

    def post(self, url, data, headers={}):
        return self.send(url, 'POST', data, headers=headers)

    def put(self, url, data, headers={}):
        return self.send(url, 'PUT', data, headers=headers)

    def delete(self, url, headers={}):
        return self.send(url, 'DELETE', headers=headers)
