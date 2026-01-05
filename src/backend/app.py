from flask import Flask, request, jsonify, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
from datetime import datetime, timedelta

# store database next to this file so relative cwd won't break
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'database.db')
# ensure folder exists
os.makedirs(BASE_DIR, exist_ok=True)

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        id_number TEXT NOT NULL,
        email TEXT,
        balance REAL DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS credit_card_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        id_number TEXT NOT NULL,
        annual_income REAL,
        card_type TEXT,
        status TEXT DEFAULT 'received',
        created_at TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        created_at TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TEXT,
        expires_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    db.commit()


def create_session(user_id, hours_valid=24):
    db = get_db()
    cur = db.cursor()
    token = secrets.token_urlsafe(32)
    created = datetime.utcnow()
    expires = created + timedelta(hours=hours_valid)
    cur.execute('''INSERT INTO sessions (user_id, token, created_at, expires_at) VALUES (?,?,?,?)''', (
        user_id, token, created.isoformat(), expires.isoformat()
    ))
    db.commit()
    return token


def get_user_by_token(token):
    if not token:
        return None
    db = get_db()
    cur = db.cursor()
    cur.execute('''SELECT u.* FROM users u JOIN sessions s ON s.user_id = u.id WHERE s.token = ?''', (token,))
    user = cur.fetchone()
    if not user:
        return None
    # verify not expired
    cur.execute('SELECT expires_at FROM sessions WHERE token = ?', (token,))
    row = cur.fetchone()
    if not row:
        return None
    try:
        expires = datetime.fromisoformat(row['expires_at'])
    except Exception:
        return None
    if datetime.utcnow() > expires:
        # session expired -> remove
        cur.execute('DELETE FROM sessions WHERE token = ?', (token,))
        db.commit()
        return None
    return user

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/api/accounts/open', methods=['POST'])
def open_account():
    data = request.get_json() or {}
    required = ['full_name', 'id_number', 'initial_deposit']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('''INSERT INTO accounts (full_name, id_number, email, balance, status, created_at)
                   VALUES (?,?,?,?,?,?)''', (
        data.get('full_name'), data.get('id_number'), data.get('email'), float(data.get('initial_deposit') or 0), 'pending', datetime.utcnow().isoformat()
    ))
    db.commit()
    account_id = cur.lastrowid
    return jsonify({'account_id': account_id, 'status': 'pending', 'message': '申請已建立，等待審核'}), 201

@app.route('/api/creditcards/apply', methods=['POST'])
def apply_creditcard():
    data = request.get_json() or {}
    required = ['full_name', 'id_number', 'annual_income', 'card_type']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('''INSERT INTO credit_card_applications (full_name, id_number, annual_income, card_type, status, created_at)
                   VALUES (?,?,?,?,?,?)''', (
        data.get('full_name'), data.get('id_number'), float(data.get('annual_income') or 0), data.get('card_type'), 'received', datetime.utcnow().isoformat()
    ))
    db.commit()
    application_id = cur.lastrowid
    return jsonify({'application_id': application_id, 'status': 'received', 'message': '信用卡申請已收到'}), 201

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    required = ['username', 'password', 'email']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    username = data.get('username')
    password = data.get('password')
    password_hash = generate_password_hash(password)
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute('''INSERT INTO users (username, password_hash, email, created_at) VALUES (?,?,?,?)''', (
            username, password_hash, data.get('email'), datetime.utcnow().isoformat()
        ))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'username already exists'}), 409
    user_id = cur.lastrowid
    return jsonify({'user_id': user_id, 'username': username, 'message': '註冊成功'}), 201


@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    required = ['username', 'password']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'invalid credentials'}), 401
    token = create_session(user['id'])
    return jsonify({'token': token, 'user_id': user['id'], 'username': user['username'], 'message': '登入成功'}), 200


@app.route('/api/users/logout', methods=['POST'])
def logout_user():
    # Accept token via Authorization header or JSON body
    auth = request.headers.get('Authorization', '')
    token = None
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1]
    else:
        data = request.get_json(silent=True) or {}
        token = data.get('token')
    if not token:
        return jsonify({'error': 'missing token'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('DELETE FROM sessions WHERE token = ?', (token,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({'error': 'invalid token'}), 401
    return jsonify({'message': '登出成功'}), 200


@app.route('/api/accounts', methods=['GET'])
def list_accounts():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    offset = (page - 1) * per_page
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) AS cnt FROM accounts')
    total = cur.fetchone()['cnt']
    cur.execute('SELECT * FROM accounts ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset))
    rows = cur.fetchall()
    items = [dict(r) for r in rows]
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    return jsonify({'items': items, 'page': page, 'per_page': per_page, 'total': total, 'total_pages': total_pages}), 200


@app.route('/api/creditcards', methods=['GET'])
def list_creditcards():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    try:
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        per_page = 10
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    offset = (page - 1) * per_page
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) AS cnt FROM credit_card_applications')
    total = cur.fetchone()['cnt']
    cur.execute('SELECT * FROM credit_card_applications ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset))
    rows = cur.fetchall()
    items = [dict(r) for r in rows]
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    return jsonify({'items': items, 'page': page, 'per_page': per_page, 'total': total, 'total_pages': total_pages}), 200

if __name__ == '__main__':
    with app.app_context():
        init_db()
    # Respect FLASK_DEBUG environment variable; default to False for safety
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)