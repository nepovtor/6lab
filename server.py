from flask import Flask, request, jsonify
import sqlite3

DB_NAME = 'store.db'


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


@app.route('/items', methods=['GET'])
def list_items():
    with connect_db() as conn:
        cur = conn.execute("SELECT * FROM items")
        items = [dict(row) for row in cur.fetchall()]
    return jsonify(items)


@app.route('/items', methods=['POST'])
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
