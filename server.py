from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import json, sqlite3, secrets, os
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'links.sqlite3'

@contextmanager
def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, url TEXT NOT NULL, clicks INTEGER NOT NULL DEFAULT 0)')

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, kind='application/json; charset=utf-8'):
        data = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            return self.send(200, (ROOT / 'index.html').read_text(encoding='utf-8'), 'text/html; charset=utf-8')
        if path == '/api/links':
            with connect() as db:
                rows = db.execute('SELECT code, url, clicks FROM links ORDER BY rowid DESC LIMIT 50').fetchall()
            return self.send(200, json.dumps([dict(row) for row in rows]))
        code = path.removeprefix('/')
        with connect() as db:
            row = db.execute('SELECT url FROM links WHERE code = ?', (code,)).fetchone()
            if row:
                db.execute('UPDATE links SET clicks = clicks + 1 WHERE code = ?', (code,))
        if not row:
            return self.send(404, 'Link não encontrado.', 'text/plain; charset=utf-8')
        self.send_response(302)
        self.send_header('Location', row['url'])
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/links':
            return self.send(404, '{}')
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > 12000:
                raise ValueError('Requisição inválida.')
            url = json.loads(self.rfile.read(size)).get('url', '').strip()
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or any(ord(c) <= 32 or ord(c) == 127 for c in url) or len(url) > 8000:
                raise ValueError('Digite uma URL válida começando com https:// ou http://.')
            with connect() as db:
                for attempt in range(10):
                    code = secrets.token_urlsafe(5)
                    try:
                        db.execute('INSERT INTO links (code, url) VALUES (?, ?)', (code, url))
                        break
                    except sqlite3.IntegrityError:
                        continue
                else:
                    raise ValueError('Tente novamente.')
            self.send(201, json.dumps({'code': code, 'url': url, 'clicks': 0}))
        except (ValueError, TypeError, AttributeError):
            self.send(400, json.dumps({'error': 'Digite uma URL válida começando com https:// ou http://.'}))

if __name__ == '__main__':
    initialize()
    port = int(os.environ.get('PORT', '8000'))
    print(f'Encurtador disponível em http://localhost:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
