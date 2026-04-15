from flask import Flask, jsonify, request, session, send_from_directory
import json, os, datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dustin-downs-bars-2026')

SPECIALS_FILE = '/data/ogden_special.json'
MANAGER_PASSWORD = os.environ.get('MANAGER_PASSWORD', 'ogden2026')

def load_special():
    if os.path.exists(SPECIALS_FILE):
        with open(SPECIALS_FILE) as f:
            return json.load(f)
    return {"title": "", "description": "", "price": "", "updated": ""}

def save_special(data):
    os.makedirs('/data', exist_ok=True)
    data['updated'] = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
    with open(SPECIALS_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/special', methods=['GET'])
def get_special():
    return jsonify(load_special())

@app.route('/api/special', methods=['POST'])
def set_special():
    if not session.get('manager'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    save_special({
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'price': data.get('price', '')
    })
    return jsonify({'success': True, 'special': load_special()})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == MANAGER_PASSWORD:
        session['manager'] = True
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('manager', None)
    return jsonify({'success': True})

@app.route('/api/auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': bool(session.get('manager'))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
