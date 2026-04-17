from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'downtown-bars-2026')

# Try /data (Render persistent disk); fall back to ./data/ for local dev
def _resolve_data_dir():
    candidate = os.environ.get('DATA_DIR', '/data')
    try:
        os.makedirs(candidate, exist_ok=True)
        test = os.path.join(candidate, '.write_test')
        with open(test, 'w') as f:
            f.write('ok')
        os.remove(test)
        return candidate
    except OSError:
        fallback = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(fallback, exist_ok=True)
        return fallback

DATA_DIR = _resolve_data_dir()

ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', 'downtown2026')
ADMIN_USER     = os.environ.get('ADMIN_USER', 'admin')

# Return JSON for any unhandled 500 so clients don't get an HTML parse error
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': str(e)}), 500

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

def load_accounts():
    return load_json('accounts.json', [])

def save_accounts(accounts):
    save_json('accounts.json', accounts)

def authenticate(username, password):
    """Return (role, username, permissions).
    Admin: ('admin', ADMIN_USER, None)  — None means bypass all permission checks.
    Manager: ('manager', username, [...])
    Failure: (None, None, None)
    """
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        return 'admin', ADMIN_USER, None
    for acct in load_accounts():
        if acct['username'] == username and check_password_hash(acct['password_hash'], password):
            perms = acct.get('permissions', ['specials', 'menu'])
            return 'manager', acct['username'], perms
    return None, None, None

def default_menus():
    return {
        "alibi": {
            "special": {"title": "", "description": "", "price": "", "updated": ""},
            "events": [],
            "menu": {
                "Appetizers": [
                    {"name": "Homemade Fries", "description": "", "price": "3.75"},
                    {"name": "Beer Battered Fries", "description": "", "price": "4.95"},
                    {"name": "Deep-Fried Pickles", "description": "", "price": "5.45"},
                    {"name": "Chicken Strips (3-4)", "description": "", "price": "7.45"},
                    {"name": "Chicken Wings (6)", "description": "", "price": "7.95"},
                    {"name": "Fiesta Poppers", "description": "", "price": "6.95"},
                    {"name": "White or Yellow Curds", "description": "", "price": "6.95"},
                    {"name": "Broccoli Bites (5)", "description": "", "price": "6.45"},
                    {"name": "Onion Rings", "description": "", "price": "6.45"},
                    {"name": "Deep-Fried Mushrooms", "description": "", "price": "5.85"},
                    {"name": "Elephant Ear", "description": "", "price": "5.95"},
                    {"name": "Crab Rangoons (4)", "description": "", "price": "5.95"}
                ],
                "Burgers": [
                    {"name": "Hamburger*", "description": "", "price": "5.95"},
                    {"name": "Cheeseburger*", "description": "", "price": "5.95"},
                    {"name": "Grilled Cheeseburger*", "description": "", "price": "6.95"},
                    {"name": "Linda's Mushroom Swiss*", "description": "", "price": "7.45"},
                    {"name": "The Alibi Burger*", "description": "2 1/4lb Patties, 5 Onion Rings, 3 Pieces of Bacon, American, topped with BBQ Sauce", "price": "10.95"},
                    {"name": "AM/PM Burger*", "description": "1/4lb, Egg, Bacon & American Cheese, served on top of a Hashbrown", "price": "9.45"},
                    {"name": "Patty Melt*", "description": "1/4lb Burger, 2 Slices of Swiss Cheese and Fried Onions on Texas Toast", "price": "7.95"},
                    {"name": "Jalapeno Bacon Ranch*", "description": "2 1/4lb Patties, 3 Pieces of Bacon, Smothered with Ranch & topped with Jalapenos and Swiss Cheese", "price": "10.95"},
                    {"name": "Madness Burger*", "description": "2 1/4lb Patties topped with Fried Cheese Curds, Deep-Fried Pickles & American Cheese", "price": "9.95"}
                ],
                "Burger Add-Ons": [
                    {"name": "Add Lettuce, Tomato or Fried Onion", "description": "", "price": "+.95"},
                    {"name": "Add Bacon", "description": "", "price": "+1.95"},
                    {"name": "Double Your Patty*", "description": "", "price": "+2.45"}
                ],
                "Tacos, Sammiches & More": [
                    {"name": "Homemade Taco", "description": "Taco Meat Contains Beans. Make it Supreme +.95", "price": "2.95"},
                    {"name": "Beef Gordita", "description": "Taco Meat Contains Beans. Make it Supreme +.95", "price": "4.45"},
                    {"name": "Grilled Cheese", "description": "", "price": "5.95"},
                    {"name": "BLT", "description": "", "price": "6.95"},
                    {"name": "Chicago Style Gyro", "description": "Authentic Hard-shaved Gyro Meat, served with Tomatoes and Onions, Topped with our famous Tzatziki Sauce", "price": "8.95"},
                    {"name": "Italian Beef", "description": "Fontanini Beef, Sweet Peppers and Mozzarella Cheese. Served on a 6\" Grilled Hoagie with a Side of Au Jus", "price": "10.95"},
                    {"name": "French Dip", "description": "Fontanini Beef & melted Swiss Cheese served on a 6\" Grilled Hoagie with a Side of Au Jus", "price": "10.45"},
                    {"name": "Grilled Chicken Sandwich", "description": "5oz Tender Chicken Breast topped with Lettuce, Tomato & Mayo", "price": "8.95"},
                    {"name": "Loaded Nachos", "description": "Homemade Nacho Chips topped with Taco Meat, Tomatoes, Black Olives, Lettuce, Cheese, Jalapenos, Onions & Sweet Peppers", "price": "10.95"},
                    {"name": "Indian Taco (Ma's Fry Bread)", "description": "Seasoned Meat, Tomatoes, Lettuce, Cheese, Jalapenos, Black Olives, Onions & Sweet Peppers", "price": "10.95"}
                ],
                "Salads": [
                    {"name": "House Salad", "description": "", "price": "7.45"},
                    {"name": "Caesar Salad", "description": "", "price": "8.95"},
                    {"name": "Chicken Bacon Ranch Salad", "description": "", "price": "8.95"},
                    {"name": "Gyro Salad", "description": "", "price": "9.95"},
                    {"name": "Taco Salad", "description": "", "price": "9.95"}
                ],
                "Pizza": [
                    {"name": "10\" Cheese & Sauce", "description": "Toppings 1.75 each. Available: Pepperoni, Sausage, Hamburger, Bacon, Onions, Black Olives, Green Olives, Tomatoes, Mushrooms, Green Peppers, Sweet Peppers", "price": "10.95"},
                    {"name": "12\" Cheese & Sauce", "description": "Toppings 1.50 each", "price": "13.95"},
                    {"name": "16\" Cheese & Sauce", "description": "Toppings 1.75 each", "price": "17.95"},
                    {"name": "Roger's Special", "description": "Black Olives, Onions, Sausage, Hamburger & Mushrooms", "price": "18.95 / 18.95 / 24.95"},
                    {"name": "Bacon Cheeseburger Pizza", "description": "Hamburger, Cheese, Onions, Bacon & Pickles", "price": "18.95 / 18.95 / 22.95"},
                    {"name": "Gyro Pizza", "description": "Lamb, Onions, Tomatoes, Cheese, Side of Tzatziki Sauce", "price": "19.95 / 19.95 / 22.95"},
                    {"name": "Cauliflower Crust (12\", 3 toppings)", "description": "", "price": "13.95"}
                ],
                "Weekly Specials": [
                    {"name": "Monday: P.B. Bacon Burger* with Fries", "description": "", "price": "8.95"},
                    {"name": "Tuesday: 2 Tacos", "description": "", "price": "4.50"},
                    {"name": "Tuesday: Indian Taco", "description": "", "price": "8.95"},
                    {"name": "Wednesday: Loaded Nachos", "description": "", "price": "8.95"},
                    {"name": "Wednesday: Gyros To-Go", "description": "", "price": "5.95"},
                    {"name": "Thursday: Italian Beef or French Dip", "description": "", "price": "6.95"},
                    {"name": "Friday: 2 Cheeseburgers* & 12\" 3-Topping Pizza", "description": "", "price": "8.95"}
                ]
            }
        },
        "ogden": {
            "special": {"title": "", "description": "", "price": "", "updated": ""},
            "events": [],
            "menu": {
                "Appetizers & More": [
                    {"name": "Wisconsin White Cheese Curds", "description": "6oz, Tossed in Buffalo Sauce, Topped with Buttermilk Ranch and Bleu Cheese", "price": "9"},
                    {"name": "Red & Bleu Curds", "description": "Tossed in Buffalo Sauce, Topped with Bleu Cheese", "price": "11"},
                    {"name": "Black & White Curds", "description": "Tossed in a Balsamic Glaze with Feta Cheese, topped with Bacon Crumbles", "price": "12"},
                    {"name": "Sweet Chili Curds", "description": "Tossed in Sweet Chili Sauce and Feta Cheese, served with Buttermilk Ranch", "price": "12"},
                    {"name": "Guacamole & Chips", "description": "Made Fresh to Order with Pico de Gallo, Avocado and Homemade Tortilla Chips", "price": "10"},
                    {"name": "Freshly Cut French Fries", "description": "", "price": "4"},
                    {"name": "Garlic Parmesan French Fries", "description": "", "price": "5"},
                    {"name": "Cajun or Sweet Potato Fries", "description": "", "price": "5"},
                    {"name": "Chicken Quesadilla", "description": "Flour Tortilla with Grilled Chicken Breast, Pico de Gallo, Mozzarella Cheese, Salsa & Sour Cream", "price": "12"},
                    {"name": "Crab Rangoons", "description": "5 Rangoons served with Sweet & Sour or Sweet Chili Sauce", "price": "9"},
                    {"name": "Lobster Cakes", "description": "2 Homemade Lobster Cakes Served with our Famous Zesty Sauce", "price": "14"},
                    {"name": "Fantail Shrimp", "description": "5 Jumbo Fantail, served with Cocktail Sauce", "price": "12"},
                    {"name": "Chicken Wings", "description": "8 Bone-In Wings tossed in your choice of Sauce: Buffalo, BBQ, Teriyaki or Sweet Chili", "price": "10"},
                    {"name": "Chicken Strips (3-4)", "description": "", "price": "5"}
                ],
                "Burgers, Wraps & Sandwiches": [
                    {"name": "Grilled Cheeseburger*", "description": "1/4lb Burger, 2 Slices of Cheese, on Your Choice of Texas Toast or Marble Rye", "price": "8"},
                    {"name": "Cheeseburger*", "description": "1/4lb Burger, 2 Slices of Swiss Cheese, Sauteed Mushrooms & Onions, Roasted Peppers, Your Choice of Texas Toast", "price": "9"},
                    {"name": "Patty Melt*", "description": "1/4lb Burger, 2 Slices of Swiss Cheese, Roasted Peppers on Your Choice of Texas Toast or Marble Rye", "price": "12"},
                    {"name": "Avocado Pico Burger*", "description": "1/4lb Burger topped with Mozzarella Cheese, Pico de Gallo, and Avocado", "price": "14"},
                    {"name": "Wild Rice Burger", "description": "Homemade Wild Rice Patty topped with Spinach, Onion, Tomato and Our Homemade Zesty Sauce", "price": "12"},
                    {"name": "Jac'd Bacon & Bleu Cheeseburger*", "description": "1/4lb Burger topped with Jac Apple Bacon Jam and Bleu Cheese Crumbles", "price": "13"},
                    {"name": "Lobster Sandwich", "description": "Avocado Cake, Spinach, Tomato, Cucumber and Zesty Sauce on a Bun", "price": "13"},
                    {"name": "BLT", "description": "6 Pieces of Bacon, Lettuce, Tomato & Mayo with Your Choice of Texas Toast or Marble Rye", "price": "12"},
                    {"name": "Chicken Bacon Ranch Wrap or Sandwich", "description": "Grilled Chicken, Bacon, Cheddar & Ranch in a Grilled Flour Tortilla", "price": "11"},
                    {"name": "Buffalo Chicken Wrap", "description": "Grilled Chicken, Spinach, Avocado, Bleu Cheese, Pico de Gallo, Buffalo Sauce in a Grilled Flour Tortilla", "price": "12"},
                    {"name": "Chicken Caesar Wrap", "description": "Grilled Chicken, Lettuce, Parmesan Cheese, Homemade Caesar Croutons in a Grilled Flour Tortilla", "price": "12"},
                    {"name": "Italian Beef", "description": "Grilled Italian Hoagie with Sweet Peppers & Mozzarella Cheese, Served with a Side of Au Jus", "price": "13"},
                    {"name": "Sweet Heat Wrap", "description": "Grilled Chicken, Red Onions, Shaved Carrots, Spinach in a Grilled Flour Tortilla with Sweet Thai Sauce", "price": "13"},
                    {"name": "Steak & Beef Wrap", "description": "Thinly Sliced Steak, Roasted Beets, Red Onions, Feta Cheese, Spinach, Brown Butter Dressing in a Grilled Flour Tortilla", "price": "12"},
                    {"name": "French Dip", "description": "Fontanini Beef, Melted Swiss Cheese, Served on a 6\" Grilled Hoagie with a Side of Au Jus", "price": "12"},
                    {"name": "Chicago Style Gyro", "description": "Authentic Hard-Shaved Gyro Meat, Tomatoes, Onions, Cilantro & Feta Cheese, topped with Homemade Tzatziki Sauce", "price": "12"}
                ],
                "Pizza": [
                    {"name": "Pizza Your Way! (1 Topping)", "description": "Choose 12\" or 16\"", "price": "17 / 25"},
                    {"name": "Pizza Your Way! (2 Toppings)", "description": "Choose 12\" or 16\"", "price": "19 / 25"},
                    {"name": "Classic Supreme", "description": "Pepperoni, Sausage, Greek Olives, Red Onion, Tomato and Mushrooms. 12\" or 16\"", "price": "18 / 23"},
                    {"name": "Sweet & Spicy Hawaiian", "description": "Mozzarella, Ham, Pineapple, Red Peppers and Jalapeños, Topped with Sweet Chili Sauce. 12\" or 16\"", "price": "19 / 25"},
                    {"name": "Veggie", "description": "Red or White Sauce, Greek Olives, Red & Green Peppers, Red Onions, Tomato, Mushrooms, Artichoke Hearts. 12\" or 16\"", "price": "19 / 25"},
                    {"name": "Steak & Feta", "description": "Garlic White Sauce, Thinly Sliced Tenderloin, Portabella Mushrooms, Caramelized Onion, Spinach, Feta Cheese, Peppercorn Ranch. 12\" or 16\"", "price": "20 / 26"},
                    {"name": "BBQ Chicken, Bacon & Bleu Cheese", "description": "BBQ Sauce, Mozzarella, Grilled Chicken, Bacon, Red Onions, Bleu Cheese. 12\" or 16\"", "price": "14 / 17"}
                ],
                "Flatbread": [
                    {"name": "Margherita", "description": "Basil Marinara Sauce, Mozzarella and Parmesan, topped with Basil and Balsamic Glaze", "price": "9"},
                    {"name": "Thai Peanut", "description": "Grilled Chicken on Our Special Thai Peanut Sauce, Drizzled with Sweet Chili Sauce and Cilantro", "price": "11"},
                    {"name": "B.L.T.A.", "description": "Crispy Bacon, Chopped Lettuce, and Tomatoes Drizzled with Our Avocado Mayo", "price": "12"},
                    {"name": "White Chicken", "description": "Homemade Garlic White Sauce, Mozzarella, Spinach, Grilled Chicken, Bacon, Red Onions and Parmesan Cheese", "price": "12"},
                    {"name": "Gyro", "description": "Gyro Meat, Tomatoes, Onions, Feta Cheese, Cilantro and Your Choice of Red Sauce or Tzatziki", "price": "13"}
                ],
                "Salads & Soups": [
                    {"name": "Greek Salad", "description": "Mixed Greens, Artichoke Hearts, Greek Olives, Red Onions, Sweet Peppers, and Feta Cheese tossed in Greek Dressing", "price": "14"},
                    {"name": "Caesar Salad", "description": "Fresh Romaine Lettuce, Tomatoes, Homemade Croutons, Parmesan Cheese & Caesar Dressing", "price": "12"},
                    {"name": "Market Salad", "description": "Mixed Greens, Tomatoes, Hardboiled Eggs, Bacon, Bleu Cheese, Red Onions, Carrots with a Side of Dressing", "price": "14"},
                    {"name": "House Salad", "description": "Fresh Romaine Lettuce, Red Onions, Tomatoes, Homemade Croutons with Your Choice of Dressing", "price": "8"},
                    {"name": "Add Grilled Chicken or Gyro Meat", "description": "Add to any salad", "price": "+4"},
                    {"name": "Baked French Onion Soup", "description": "Chef's Special — Cup or Bowl", "price": "4 / 7"}
                ],
                "For the Kids": [
                    {"name": "Grilled Cheese", "description": "2 Slices of American Cheese, Melted on Texas Toast", "price": "5"},
                    {"name": "Cheese Quesadilla", "description": "Melted Mozzarella Cheese on a Flour Tortilla, Served with Salsa & Sour Cream", "price": "6"},
                    {"name": "Chicken Strip Basket with French Fries", "description": "", "price": "7"},
                    {"name": "6\" Personal Pizza (Up to 2 Toppings)", "description": "Choice of Sausage, Onion, Mushroom or Pepperoni", "price": "6"}
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
    perms = session.get('permissions')
    if perms is not None and 'specials' not in perms:
        return jsonify({'error': 'Insufficient permissions'}), 403
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
    perms = session.get('permissions')
    if perms is not None and 'menu' not in perms:
        return jsonify({'error': 'Insufficient permissions'}), 403
    if bar not in ('ogden', 'alibi'):
        return jsonify({'error': 'Unknown bar'}), 404
    data = load_bar_data()
    data[bar]['menu'] = request.json.get('menu', data[bar]['menu'])
    save_bar_data(data)
    return jsonify({'success': True})

@app.route('/api/bars/<bar>/events', methods=['POST'])
def set_events(bar):
    if not session.get('manager'):
        return jsonify({'error': 'Unauthorized'}), 401
    if bar not in ('ogden', 'alibi'):
        return jsonify({'error': 'Unknown bar'}), 404
    data = load_bar_data()
    data[bar]['events'] = request.json.get('events', [])
    save_bar_data(data)
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def login():
    body = request.json or {}
    role, username, permissions = authenticate(body.get('username', ''), body.get('password', ''))
    if role:
        session['manager']     = True
        session['role']        = role
        session['username']    = username
        session['permissions'] = permissions
        return jsonify({'success': True, 'role': role, 'username': username, 'permissions': permissions})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth', methods=['GET'])
def check_auth():
    return jsonify({
        'authenticated': bool(session.get('manager')),
        'role':          session.get('role', 'manager'),
        'username':      session.get('username', ''),
        'permissions':   session.get('permissions')
    })

# ── account management (admin only) ───────────────────────────────────────────

@app.route('/api/accounts', methods=['GET'])
def list_accounts():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify([
        {'username': a['username'], 'permissions': a.get('permissions', ['specials', 'menu'])}
        for a in load_accounts()
    ])

@app.route('/api/accounts', methods=['POST'])
def create_account():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    body     = request.json or {}
    username = body.get('username', '').strip()
    password = body.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    accounts = load_accounts()
    if any(a['username'] == username for a in accounts):
        return jsonify({'error': 'That username already exists'}), 400
    accounts.append({
        'username':      username,
        'password_hash': generate_password_hash(password),
        'permissions':   ['specials', 'menu']
    })
    save_accounts(accounts)
    return jsonify({'success': True})

@app.route('/api/accounts/<username>', methods=['DELETE'])
def delete_account(username):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    accounts = [a for a in load_accounts() if a['username'] != username]
    save_accounts(accounts)
    return jsonify({'success': True})

@app.route('/api/accounts/<username>/permissions', methods=['PUT'])
def update_permissions(username):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    body  = request.json or {}
    perms = body.get('permissions', ['specials', 'menu'])
    if not isinstance(perms, list):
        return jsonify({'error': 'Invalid permissions format'}), 400
    accounts = load_accounts()
    updated  = False
    for acct in accounts:
        if acct['username'] == username:
            acct['permissions'] = perms
            updated = True
            break
    if not updated:
        return jsonify({'error': 'Account not found'}), 404
    save_accounts(accounts)
    return jsonify({'success': True, 'permissions': perms})

@app.route('/api/accounts/<username>/password', methods=['PUT'])
def reset_password(username):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    body     = request.json or {}
    new_pass = body.get('password', '')
    if not new_pass:
        return jsonify({'error': 'Password is required'}), 400
    accounts = load_accounts()
    updated  = False
    for acct in accounts:
        if acct['username'] == username:
            acct['password_hash'] = generate_password_hash(new_pass)
            updated = True
            break
    if not updated:
        return jsonify({'error': 'Account not found'}), 404
    save_accounts(accounts)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
