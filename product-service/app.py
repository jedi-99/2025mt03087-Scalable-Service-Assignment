from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Wireless Mouse', 25.50, 100)")
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Mechanical Keyboard', 85.00, 50)")
    conn.commit()
    conn.close()

@app.route('/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price, stock FROM products')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'name': r[1], 'price': r[2], 'stock': r[3]} for r in rows]), 200

@app.route('/products/<int:item_id>', methods=['GET'])
def get_product(item_id):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price, stock FROM products WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'id': row[0], 'name': row[1], 'price': row[2], 'stock': row[3]}), 200
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
                   (data['name'], data['price'], data['stock']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'status': 'Created'}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)