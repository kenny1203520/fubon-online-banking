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
    # if upgrading an existing DB, add new columns safely
    try:
        cur.execute("ALTER TABLE accounts ADD COLUMN cashless_enabled INTEGER DEFAULT 0")
    except Exception:
        pass
    # ensure transactions table has expected columns for newer code
    try:
        cur.execute("ALTER TABLE transactions ADD COLUMN related_account INTEGER")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT 'TWD'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE transactions ADD COLUMN description TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE transactions ADD COLUMN created_at TEXT")
    except Exception:
        pass
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
    CREATE TABLE IF NOT EXISTS credit_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        card_number TEXT UNIQUE,
        limit_amount REAL DEFAULT 0,
        balance_due REAL DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS credit_card_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        created_at TEXT,
        FOREIGN KEY(card_id) REFERENCES credit_cards(id)
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
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'TWD',
        related_account INTEGER,
        description TEXT,
        created_at TEXT,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        product_id TEXT,
        amount REAL NOT NULL,
        created_at TEXT,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'applied',
        created_at TEXT,
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


@app.route('/api/accounts/balance', methods=['POST'])
def account_balance():
    data = request.get_json() or {}
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({'error': 'missing account_id'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, balance, cashless_enabled FROM accounts WHERE id = ?', (account_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'account not found'}), 404
    return jsonify({'account_id': row['id'], 'balance': row['balance'], 'cashless_enabled': bool(row['cashless_enabled'])}), 200


@app.route('/api/accounts/transactions', methods=['POST'])
def account_transactions():
    data = request.get_json() or {}
    account_id = data.get('account_id')
    if not account_id:
        return jsonify({'error': 'missing account_id'}), 400
    frm = data.get('from')
    to = data.get('to')
    db = get_db()
    cur = db.cursor()
    q = 'SELECT * FROM transactions WHERE account_id = ?'
    params = [account_id]
    if frm:
        q += ' AND created_at >= ?'
        params.append(frm)
    if to:
        q += ' AND created_at <= ?'
        params.append(to)
    q += ' ORDER BY id DESC LIMIT 100'
    cur.execute(q, tuple(params))
    rows = cur.fetchall()
    items = [dict(r) for r in rows]
    return jsonify({'items': items}), 200


@app.route('/api/accounts/transfer', methods=['POST'])
def account_transfer():
    data = request.get_json() or {}
    required = ['from_account', 'to_account', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'invalid amount'}), 400
    if amount <= 0:
        return jsonify({'error': 'amount must be positive'}), 400
    from_id = data.get('from_account')
    to_id = data.get('to_account')
    currency = data.get('currency') or 'TWD'
    db = get_db()
    cur = db.cursor()
    # fetch balances
    cur.execute('SELECT id, balance FROM accounts WHERE id = ?', (from_id,))
    src = cur.fetchone()
    cur.execute('SELECT id, balance FROM accounts WHERE id = ?', (to_id,))
    dst = cur.fetchone()
    if not src or not dst:
        return jsonify({'error': 'source or destination account not found'}), 404
    if src['balance'] < amount:
        return jsonify({'error': 'insufficient funds'}), 400
    # perform transfer
    new_src = src['balance'] - amount
    new_dst = dst['balance'] + amount
    cur.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_src, from_id))
    cur.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_dst, to_id))
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO transactions (account_id, type, amount, currency, related_account, description, created_at) VALUES (?,?,?,?,?,?,?)', (from_id, 'debit', -amount, currency, to_id, 'transfer out', now))
    cur.execute('INSERT INTO transactions (account_id, type, amount, currency, related_account, description, created_at) VALUES (?,?,?,?,?,?,?)', (to_id, 'credit', amount, currency, from_id, 'transfer in', now))
    db.commit()
    return jsonify({'message': 'transfer completed', 'from_new_balance': new_src, 'to_new_balance': new_dst}), 200


@app.route('/api/accounts/cashless_withdraw', methods=['POST'])
def account_cashless():
    data = request.get_json() or {}
    account_id = data.get('account_id')
    enabled = data.get('enabled')
    if account_id is None or enabled is None:
        return jsonify({'error': 'missing account_id or enabled flag'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute('UPDATE accounts SET cashless_enabled = ? WHERE id = ?', (1 if enabled else 0, account_id))
    db.commit()
    return jsonify({'account_id': account_id, 'cashless_enabled': bool(enabled)}), 200


@app.route('/api/investments/query', methods=['POST'])
def investments_query():
    data = request.get_json() or {}
    account_id = data.get('account_id')
    db = get_db()
    cur = db.cursor()
    if account_id:
        cur.execute('SELECT * FROM investments WHERE account_id = ? ORDER BY id DESC', (account_id,))
    else:
        cur.execute('SELECT * FROM investments ORDER BY id DESC LIMIT 100')
    rows = cur.fetchall()
    items = [dict(r) for r in rows]
    return jsonify({'items': items}), 200


@app.route('/api/investments/purchase', methods=['POST'])
def investments_purchase():
    data = request.get_json() or {}
    required = ['account_id', 'product_id', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'invalid amount'}), 400
    account_id = data.get('account_id')
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    acc = cur.fetchone()
    if not acc:
        return jsonify({'error': 'account not found'}), 404
    if acc['balance'] < amount:
        return jsonify({'error': 'insufficient funds'}), 400
    # deduct and record
    new_bal = acc['balance'] - amount
    cur.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_bal, account_id))
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO investments (account_id, product_id, amount, created_at) VALUES (?,?,?,?)', (account_id, data.get('product_id'), amount, now))
    cur.execute('INSERT INTO transactions (account_id, type, amount, currency, description, created_at) VALUES (?,?,?,?,?,?)', (account_id, 'debit', -amount, 'TWD', 'investment purchase', now))
    db.commit()
    return jsonify({'message': 'purchase successful', 'new_balance': new_bal}), 200


@app.route('/api/creditcards/pay', methods=['POST'])
def creditcard_pay():
    data = request.get_json() or {}
    required = ['user_id', 'card_id', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'invalid amount'}), 400
    card_id = data.get('card_id')
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT balance_due FROM credit_cards WHERE id = ?', (card_id,))
    card = cur.fetchone()
    if not card:
        return jsonify({'error': 'card not found'}), 404
    new_due = max(0.0, card['balance_due'] - amount)
    now = datetime.utcnow().isoformat()
    cur.execute('UPDATE credit_cards SET balance_due = ? WHERE id = ?', (new_due, card_id))
    cur.execute('INSERT INTO credit_card_payments (card_id, amount, created_at) VALUES (?,?,?)', (card_id, amount, now))
    db.commit()
    return jsonify({'message': 'payment recorded', 'new_balance_due': new_due}), 200


@app.route('/api/creditcards/cash_advance', methods=['POST'])
def creditcard_cash_advance():
    data = request.get_json() or {}
    required = ['card_id', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'invalid amount'}), 400
    card_id = data.get('card_id')
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT balance_due, limit_amount FROM credit_cards WHERE id = ?', (card_id,))
    card = cur.fetchone()
    if not card:
        return jsonify({'error': 'card not found'}), 404
    # allow cash advance but not exceed limit (simple logic)
    if card['balance_due'] + amount > card['limit_amount']:
        return jsonify({'error': 'exceeds card limit'}), 400
    new_due = card['balance_due'] + amount
    now = datetime.utcnow().isoformat()
    cur.execute('UPDATE credit_cards SET balance_due = ? WHERE id = ?', (new_due, card_id))
    cur.execute('INSERT INTO transactions (account_id, type, amount, currency, description, created_at) VALUES (?,?,?,?,?,?)', (None, 'cash_advance', amount, 'TWD', f'cash advance card {card_id}', now))
    db.commit()
    return jsonify({'message': 'cash advance processed', 'new_balance_due': new_due}), 200


@app.route('/api/loans/apply', methods=['POST'])
def loans_apply():
    data = request.get_json() or {}
    required = ['user_id', 'amount']
    if not all(k in data for k in required):
        return jsonify({'error': 'missing required fields'}), 400
    try:
        amount = float(data.get('amount'))
    except Exception:
        return jsonify({'error': 'invalid amount'}), 400
    user_id = data.get('user_id')
    db = get_db()
    cur = db.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO loans (user_id, amount, status, created_at) VALUES (?,?,?,?)', (user_id, amount, 'applied', now))
    db.commit()
    loan_id = cur.lastrowid
    return jsonify({'loan_id': loan_id, 'status': 'applied', 'message': '貸款申請已提交'}), 201

if __name__ == '__main__':
    with app.app_context():
        init_db()
    # Respect FLASK_DEBUG environment variable; default to False for safety
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)