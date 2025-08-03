import json
import secrets
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from config import SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE
from models import db, User, APIData
from utils import generate_api_key, get_serial_from_content
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id') and not session.get('admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
# ---------- Routes ----------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        if uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(username=uname).first()
        if user and user.check_password(pwd):
            # Password correct, log in user
            session['user_id'] = user.id
            return redirect(url_for('user_dashboard'))
        else:
            # Invalid credentials
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if uname and pwd:
            new_user = User(username=uname, api_key=generate_api_key())
            new_user.set_password(pwd)
            db.session.add(new_user)
            db.session.commit()

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/data')
def admin_view_data():
    if not session.get('admin'):
        return redirect(url_for('login'))

    all_data = APIData.query.order_by(APIData.timestamp.desc()).all()
    return render_template('admin_data_dashboard.html', all_data=all_data)


@app.route('/dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))

    data_entries = []
    for data_entry in user.api_data:
        try:
            content = json.loads(data_entry.content)
        except Exception:
            content = None
        data_entries.append({
            'timestamp': data_entry.timestamp,
            'content': content
        })

    return render_template('user_dashboard.html', data_entries=data_entries, api_key=user.api_key)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- API Endpoint ----------
@app.route('/api/data', methods=['POST'])
def api_receive_data():
    data = request.json
    api_key = data.get('api_key')
    content = data.get('content')

    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'Invalid API key'}), 403

    # Extract serial number (assuming it’s in first dict of the list)
    serial_number = None
    if isinstance(content, list):
        first_block = content[0]
        if isinstance(first_block, dict):
            serial_number = first_block.get("Serial")

    # Serialize list content to JSON string
    serialized_content = json.dumps(content)

    new_data = APIData(
        user_id=user.id,
        content=serialized_content,
        serial_number=serial_number
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({'status': 'success'}), 200

@app.route('/dashboard/all')
@login_required
def all_serials():
    # Admin can see all, normal users see only their own data
    if session.get('admin'):
        all_data = APIData.query.all()
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        all_data = APIData.query.filter_by(user_id=user_id).all()

    serial_map = {}

    import json
    for entry in all_data:
        try:
            content = json.loads(entry.content)
        except Exception:
            continue
        serial = get_serial_from_content(content)
        if serial:
            serial_map.setdefault(serial, []).append({
                'timestamp': entry.timestamp,
                'content': content,
                'id': entry.id
            })

    sorted_serials = sorted(serial_map.items(), key=lambda x: x[0])

    return render_template('all_serials.html', serials=sorted_serials)

@app.route('/serial/<serial_number>')
def serial_detail(serial_number):
    record = SerialData.query.filter_by(serial_number=serial_number).first()
    if not record:
        return "Serial not found", 404

    data = record.data  # this is your list-of-dicts structure
    return render_template('serial_detail.html', data=data, serial=serial_number)
'''
@app.route('/dashboard/serial/<serial>')
def serial_detail(serial):
    if session.get('admin'):
        all_data = APIData.query.all()
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        all_data = APIData.query.filter_by(user_id=user_id).all()

    import json
    filtered_entries = []
    for entry in all_data:
        try:
            content = json.loads(entry.content)
        except Exception:
            continue
        s = get_serial_from_content(content)
        if s == serial:
            filtered_entries.append({
                'timestamp': entry.timestamp,
                'content': content,
                'id': entry.id
            })

    filtered_entries.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('serial_detail.html', serial=serial, entries=filtered_entries)
    '''

@app.route('/regenerate_api_key', methods=['POST'])
def regenerate_api_key():
    # Assuming you have user info stored in session or similar
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to regenerate your API key.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Generate a new API key — example uses Python secrets
    user.api_key = secrets.token_hex(16)
    db.session.commit()
    flash('API key regenerated successfully.', 'success')

    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
