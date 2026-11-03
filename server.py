from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
import os
import secrets
import sqlite3
from flask import Flask, jsonify, request, send_file, redirect

ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get('DATABASE_PATH', str(ROOT / 'links.sqlite3')))
app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 12000

@contextmanager
def connect():
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()

def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS links (code TEXT PRIMARY KEY, url TEXT NOT NULL, clicks INTEGER NOT NULL DEFAULT 0)')

@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.get('/')
def index():
    return send_file(ROOT / 'index.html')

@app.get('/healthz')
def health():
    with connect() as db:
        db.execute('SELECT 1 FROM links LIMIT 1')
    return jsonify(status='ok')

@app.get('/api/links')
def history():
    with connect() as db:
        rows = db.execute('SELECT code, url, clicks FROM links ORDER BY rowid DESC LIMIT 50').fetchall()
    return jsonify([dict(row) for row in rows])

@app.post('/api/links')
def shorten():
    body = request.get_json(silent=True)
    url = body.get('url') if isinstance(body, dict) else None
    try:
        if not isinstance(url, str):
            raise ValueError()
        url = url.strip()
        parsed = urlsplit(url)
        if (parsed.scheme not in ('http', 'https') or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or any(ord(c) <= 32 or ord(c) == 127 for c in url) or len(url) > 8000):
            raise ValueError()
        parsed.port
    except ValueError:
        return jsonify(error='Cole um link válido, começando com https:// ou http://.'), 400
    with connect() as db:
        for _ in range(10):
            code = secrets.token_urlsafe(5)
            try:
                db.execute('INSERT INTO links (code, url) VALUES (?, ?)', (code, url))
                break
            except sqlite3.IntegrityError:
                continue
        else:
            return jsonify(error='Não deu para criar o link. Tente de novo.'), 503
    return jsonify(code=code, url=url, clicks=0), 201

@app.get('/<code>')
def follow(code):
    with connect() as db:
        row = db.execute('SELECT url FROM links WHERE code = ?', (code,)).fetchone()
        if row and request.method != 'HEAD':
            db.execute('UPDATE links SET clicks = clicks + 1 WHERE code = ?', (code,))
    if row is None:
        return 'Esse link não existe ou foi removido.', 404
    return redirect(row['url'], code=302)

@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Esse endereço é grande demais.'), 413

initialize()

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get('PORT', '8000'))
    host = os.environ.get('HOST', '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1')
    print(f'Encurtaí iniciado na porta {port}. Local: http://localhost:{port}', flush=True)
    try:
        serve(app, host=host, port=port, threads=4, max_request_body_size=12000)
    except KeyboardInterrupt:
        print('Encurtaí encerrado.')
