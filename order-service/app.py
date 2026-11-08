from flask import Flask, request, jsonify
import sqlite3
import os
import requests

app = Flask(__name__)
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5001')

def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    # Inter-service synchronous REST collaboration
    try:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", timeout=5)
        if resp.status_code != 200:
            return jsonify({'error': 'Product does not exist'}), 400
        
        product = resp.json()
        if product['stock'] < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        total_price = product['price'] * quantity
    except Exception as e:
        return jsonify({'error': f'Failed to communicate with product-service: {str(e)}'}), 503

    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (product_id, quantity, total_price, status) VALUES (?, ?, ?, ?)',
                   (product_id, quantity, total_price, 'CONFIRMED'))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'order_id': order_id,
        'product_id': product_id,
        'quantity': quantity,
        'total_price': total_price,
        'status': 'CONFIRMED'
    }), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, product_id, quantity, total_price, status FROM orders WHERE id = ?', (order_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            'order_id': row[0],
            'product_id': row[1],
            'quantity': row[2],
            'total_price': row[3],
            'status': row[4]
        }), 200
    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002)