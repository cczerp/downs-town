from flask import Flask, jsonify, request, session, send_from_directory
import json, os, datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'downtown-bars-2026')

DATA_DIR = '/data'
MANAGER_PASSWORD = os.environ.get('MANAGER_PASSWORD', 'downtown2026')

# ── helpers ────────────────────────────────────────────────────────────────────

def data_path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename, default):
    path = data_path(filename)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(filename, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(data_path(filename), 'w') as f:
        json.dump(data, f, indent=2)

def default_menus():
    return {
        "ogden": {
            "special": {"title": "", "description": "", "price": "", "updated": ""},
            "menu": {
                "Appetizers": [
                    {"name": "Loaded Nachos", "description": "House chips, queso, jalapeños, pico", "price": "10.00"},
                    {"name": "Wings (6)", "description": "Choice of sauce, ranch or bleu cheese", "price": "12.00"},
                    {"name": "Mozz Sticks", "description": "Marinara dipping sauce", "price": "8.00"}
                ],
                "Burgers & Sandwiches": [
                    {"name": "Ogden Smash Burger", "description": "Double smash, American cheese, special sauce, shredded lettuce", "price": "13.00"},
                    {"name": "Bacon Cheeseburger", "description": "1/3 lb beef, cheddar, bacon, LTO", "price": "12.00"},
                    {"name": "Grilled Chicken Sandwich", "description": "Pepper jack, avocado, chipotle mayo", "price": "12.00"},
                    {"name": "Club Sandwich", "description": "Turkey, ham, bacon, swiss, LTO", "price": "11.00"}
                ],
                "Mains": [
                    {"name": "Fish & Chips", "description": "Beer battered cod, fries, coleslaw, tartar sauce", "price": "14.00"},
                    {"name": "BBQ Pulled Pork Plate", "description": "Slow smoked, fries, coleslaw", "price": "14.00"},
                    {"name": "Mac & Cheese", "description": "Four cheese blend, breadcrumb crust", "price": "10.00"}
                ],
                "Drinks": [
                    {"name": "Draft Beer (16oz)", "description": "Ask your server for today's taps", "price": "5.00"},
                    {"name": "Domestic Bottle", "description": "Bud Light, Coors Light, Miller Lite", "price": "4.00"},
                    {"name": "Well Cocktail", "description": "House spirits, your choice of mix", "price": "6.00"},
                    {"name": "Soft Drink", "description": "Pepsi products, free refills", "price": "2.50"}
                ]
            }
        },
        "alibi": {
            "special": {"title": "", "description": "", "price": "", "updated": ""},
            "menu": {
                "Starters": [
                    {"name": "Alibi Fries", "description": "Seasoned fries, signature dipping sauce", "price": "7.00"},
                    {"name": "Pretzel Bites", "description": "Beer cheese, whole grain mustard", "price": "9.00"},
                    {"name": "Jalapeño Poppers", "description": "Cream cheese stuffed, bacon wrapped", "price": "10.00"}
                ],
                "Sandwiches & Wraps": [
                    {"name": "The Alibi Burger", "description": "1/2 lb beef, cheddar, fried onion, house sauce", "price": "14.00"},
                    {"name": "BLT Club", "description": "Double decker, toasted sourdough", "price": "12.00"},
                    {"name": "Buffalo Chicken Wrap", "description": "Crispy chicken, buffalo, ranch, cheddar", "price": "12.00"}
                ],
                "Bar Bites": [
                    {"name": "Chicken Tenders (4)", "description": "Honey mustard or BBQ", "price": "12.00"},
                    {"name": "Quesadilla", "description": "Chicken or steak, salsa, sour cream", "price": "11.00"},
                    {"name": "Chili Dog", "description": "All-beef frank, house chili, cheddar, onion", "price": "9.00"}
                ],
                "Drinks": [
                    {"name": "Draft Beer (16oz)", "description": "Ask your server for today's taps", "price": "5.00"},
                    {"name": "Craft Can", "description": "Rotating selection, ask your server", "price": "6.00"},
                    {"name": "Cocktail of the Day", "description": "Ask your bartender", "price": "8.00"},
                    {"name": "Soft Drink", "description": "Pepsi products, free refills", "price": "2.50"}
                ]
            }
        }
    }

def load_bar_data():
    return load_json('bar_data.json', default_menus())

def save_bar_data(data):
    save_json('bar_data.json', data)

# ── routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/alibi/menu')
def alibi_menu_page():
    return send_from_directory('static', 'alibi-menu.html')

@app.route('/ogden/menu')
def ogden_menu_page():
    return send_from_directory('static', 'ogden-menu.html')

@app.route('/manager')
def manager_page():
    return send_from_directory('static', 'manager.html')

@app.route('/api/bars', methods=['GET'])
def get_bars():
    return jsonify(load_bar_data())

@app.route('/api/bars/<bar>/special', methods=['POST'])
def set_special(bar):
    if not session.get('manager'):
        return jsonify({'error': 'Unauthorized'}), 401
    if bar not in ('ogden', 'alibi'):
        return jsonify({'error': 'Unknown bar'}), 404
    data = load_bar_data()
    body = request.json
    data[bar]['special'] = {
        'title': body.get('title', ''),
        'description': body.get('description', ''),
        'price': body.get('price', ''),
        'updated': datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    save_bar_data(data)
    return jsonify({'success': True, 'special': data[bar]['special']})

@app.route('/api/bars/<bar>/menu', methods=['POST'])
def set_menu(bar):
    if not session.get('manager'):
        return jsonify({'error': 'Unauthorized'}), 401
    if bar not in ('ogden', 'alibi'):
        return jsonify({'error': 'Unknown bar'}), 404
    data = load_bar_data()
    data[bar]['menu'] = request.json.get('menu', data[bar]['menu'])
    save_bar_data(data)
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def login():
    body = request.json
    if body.get('password') == MANAGER_PASSWORD:
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
