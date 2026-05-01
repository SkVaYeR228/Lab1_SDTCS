from flask import Flask, request, jsonify, render_template_string
import argparse
import pymysql

app = Flask(__name__)
db_config = {}

def get_db_connection():
    return pymysql.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        cursorclass=pymysql.cursors.DictCursor
    )

def render_response(data, template_html, status=200):
    accept_header = request.headers.get('Accept', '')
    if 'text/html' in accept_header:
        return render_template_string(template_html, data=data), status, {'Content-Type': 'text/html'}
    return jsonify(data), status

@app.route('/')
def index():
    html = """
    <h1>Simple Inventory API</h1>
    <ul>
        <li>GET /health/alive</li>
        <li>GET /health/ready</li>
        <li>GET /items</li>
        <li>POST /items</li>
        <li>GET /items/&lt;id&gt;</li>
    </ul>
    """
    return html, 200, {'Content-Type': 'text/html'}

@app.route('/health/alive')
def alive():
    return "OK", 200

@app.route('/health/ready')
def ready():
    try:
        conn = get_db_connection()
        conn.ping(reconnect=True)
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Database connection failed: {e}", 500

@app.route('/items', methods=['GET', 'POST'])
def items():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        if request.is_json:
            req_data = request.get_json()
        else:
            req_data = request.form
            
        name = req_data.get('name')
        quantity = req_data.get('quantity')
        
        cursor.execute("INSERT INTO items (name, quantity) VALUES (%s, %s)", (name, quantity))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        
        response_data = {'id': item_id, 'name': name, 'quantity': quantity}
        msg_html = "<p>Item created: ID {{ data.id }}, Name: {{ data.name }}, Qty: {{ data.quantity }}</p>"
        return render_response(response_data, msg_html, 201)

    cursor.execute("SELECT id, name FROM items")
    items_list = cursor.fetchall()
    conn.close()
    
    html_template = """
    <table border="1">
        <tr><th>ID</th><th>Name</th></tr>
        {% for item in data %}
        <tr><td>{{ item.id }}</td><td>{{ item.name }}</td></tr>
        {% endfor %}
    </table>
    """
    return render_response(items_list, html_template)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, created_at FROM items WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    conn.close()
    
    if not item:
        return "Not found", 404
        
    html_template = """
    <table border="1">
        <tr><th>ID</th><th>Name</th><th>Quantity</th><th>Created At</th></tr>
        <tr><td>{{ data.id }}</td><td>{{ data.name }}</td><td>{{ data.quantity }}</td><td>{{ data.created_at }}</td></tr>
    </table>
    """
    return render_response(item, html_template)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--db-host', default='127.0.0.1')
    parser.add_argument('--db-user', required=True)
    parser.add_argument('--db-pass', required=True)
    parser.add_argument('--db-name', required=True)
    
    args = parser.parse_args()
    
    db_config['host'] = args.db_host
    db_config['user'] = args.db_user
    db_config['password'] = args.db_pass
    db_config['database'] = args.db_name
    
    app.run(host=args.interface, port=args.port)
