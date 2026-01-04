from flask import Flask, request, jsonify, g
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DB_PATH = "./src/backend/database.db"

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
    db.commit()

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

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)
