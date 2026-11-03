import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        os.environ['DATABASE_PATH'] = str(Path(cls.tmp.name) / 'links.sqlite3')
        import server
        cls.server = server
        cls.client = server.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
        os.environ.pop('DATABASE_PATH', None)

    def test_create_redirect_and_persistence(self):
        response = self.client.post('/api/links', json={'url': 'https://example.com/path?q=1'})
        self.assertEqual(response.status_code, 201)
        code = response.json['code']
        self.assertEqual(self.client.head('/' + code).status_code, 302)
        response = self.client.get('/' + code)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], 'https://example.com/path?q=1')
        rows = self.client.get('/api/links').json
        self.assertEqual(next(row for row in rows if row['code'] == code)['clicks'], 1)
        output = subprocess.check_output([
            sys.executable, '-B', '-c',
            'import server; c=server.app.test_client(); print(c.get("/api/links").json)'
        ], env=os.environ.copy(), text=True)
        self.assertIn(code, output)

    def test_invalid_requests(self):
        for body in [None, [], {'url': 42}, {'url': 'javascript:alert(1)'},
                     {'url': 'https://example.com/\r\nInjected: yes'},
                     {'url': 'https://example.com:invalid'}, {'url': 'https://user:pass@example.com'}]:
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/api/links', json=body).status_code, 400)
        self.assertEqual(self.client.post('/api/links', data='x' * 12001,
                                         content_type='application/json').status_code, 413)

    def test_pages(self):
        with self.client.get('/') as response:
            self.assertIn('Encurta'.encode(), response.data)
        self.assertEqual(self.client.get('/healthz').json, {'status': 'ok'})
        self.assertEqual(self.client.get('/missing').status_code, 404)
        self.assertEqual(self.client.get('/server.py').status_code, 404)
        self.assertEqual(self.client.get('/links.sqlite3').status_code, 404)
