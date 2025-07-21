from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime
from functools import wraps

DB_NAME = 'store.db'
SECRET_KEY = 'change-me'


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            release_year INTEGER NOT NULL
        )"""
        )
        conn.commit()


app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    if not data or data.get('username') != 'admin' or data.get('password') != 'password':
        return {'error': 'invalid credentials'}, 401
    token = jwt.encode({
        'user': data['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')
    return {'token': token}


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization', '')
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
        if not token:
            return {'error': 'token required'}, 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'error': 'invalid token'}, 401
        return func(*args, **kwargs)

    return wrapper


@app.route('/items', methods=['GET'])
@token_required
def list_items():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    search = request.args.get('q')
    offset = (page - 1) * size
    query = "SELECT * FROM items"
    params = []
    if search:
        query += " WHERE name LIKE ?"
        params.append(f"%{search}%")
    query += " LIMIT ? OFFSET ?"
    params.extend([size, offset])
    with connect_db() as conn:
        cur = conn.execute(query, tuple(params))
        items = [dict(row) for row in cur.fetchall()]
        count_q = "SELECT COUNT(*) FROM items"
        count_params = []
        if search:
            count_q += " WHERE name LIKE ?"
            count_params.append(f"%{search}%")
        total = conn.execute(count_q, tuple(count_params)).fetchone()[0]
    return jsonify({"items": items, "page": page, "size": size, "total": total})


@app.route('/items', methods=['POST'])
@token_required
def add_item():
    data = request.get_json(force=True)
    required = {'id', 'name', 'price', 'quantity', 'release_year'}
    if not data or not required <= data.keys():
        return {'error': 'missing fields'}, 400
    with connect_db() as conn:
        cur = conn.execute("SELECT id FROM items WHERE id=?", (data['id'],))
        if cur.fetchone():
            return {'error': 'item exists'}, 409
        conn.execute(
            "INSERT INTO items(id, name, price, quantity, release_year) VALUES (?, ?, ?, ?, ?)",
            (data['id'], data['name'], data['price'], data['quantity'], data['release_year'])
        )
        conn.commit()
    return {'status': 'added'}, 201


@app.route('/items/<int:item_id>', methods=['PUT'])
@token_required
def update_item(item_id):
    data = request.get_json(force=True)
    required = {'name', 'price', 'quantity', 'release_year'}
    if not data or not required <= data.keys():
        return {'error': 'missing fields'}, 400
    with connect_db() as conn:
        cur = conn.execute("SELECT id FROM items WHERE id=?", (item_id,))
        if not cur.fetchone():
            return {'error': 'not found'}, 404
        conn.execute(
            "UPDATE items SET name=?, price=?, quantity=?, release_year=? WHERE id=?",
            (data['name'], data['price'], data['quantity'], data['release_year'], item_id)
        )
        conn.commit()
    return {'status': 'updated'}


@app.route('/items/<int:item_id>', methods=['DELETE'])
@token_required
def delete_item(item_id):
    with connect_db() as conn:
        cur = conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        if cur.rowcount == 0:
            return {'error': 'not found'}, 404
        conn.commit()
    return {'status': 'deleted'}


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
