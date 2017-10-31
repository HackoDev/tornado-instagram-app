import json

from app import make_app
from tornado.testing import AsyncHTTPTestCase

app = make_app()


def clear_db(app=None):
    app.settings['db'].users.remove()
    app.settings['db'].tokens.remove()


class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        clear_db(self.get_app())
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return app

    def get_http_port(self):
        return 8888


class TestBucketHandler(TestHandlerBase):

    def test_create_something_test(self):

        data = {
            'client_info': 'curl agent',
            'platform': 'web'
        }
        response = self.fetch(
            '/api/handshake',
            headers={'Content-Type': 'application/json'},
            method='POST',
            body=json.dumps(data),
            follow_redirects=False
        )

        self.assertEqual(response.code, 200)
        response_json = json.loads(response.body.decode())
        self.assertIn('token', response_json)
