import json
import secrets

from flask import Blueprint, session, redirect, url_for, request, flash, jsonify

from config import MASTER_API_KEY
from models import db, User, APIData, BatData

api_bp = Blueprint("api", __name__)

def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

'''
        API
'''

def check_api_key(api_key):
    # Master API key bypass
    if api_key == MASTER_API_KEY:
        user = None  # Admin/master submission
    else:
        user = User.query.filter(User.api_keys.any()).all()
        user = next((u for u in user if u.check_api_key(api_key)), None)
        if not user:
            return False
    return True

@api_bp.route('/api/results', methods=['POST'])
def api_receive_data():
    data = request.json
    api_key = data.get('api_key')
    name = data.get('name')
    specs = data.get('specs')
    serial_number = data.get('serial_number')
    test_results = data.get('test_results')

    # Master API key bypass
    if api_key == MASTER_API_KEY:
        user = None  # Admin/master submission
    else:
        user = User.query.filter(User.api_keys.any()).all()
        user = next((u for u in user if u.check_api_key(api_key)), None)
        if not user:
            return jsonify({'error': 'Invalid API key'}), 403

    serialized_specs = json.dumps(specs)
    serialized_test_results = json.dumps(test_results)
    new_data = APIData(
        user_id=user.id if user else None,
        serial_number=serial_number,
        name=name,
        specs=serialized_specs,
        test_results=serialized_test_results
    )

    db.session.add(new_data)
    db.session.commit()
    return jsonify({'status': 'success'}), 200

@api_bp.route('/api/battery', methods=['POST'])
def battery_receive_data():
    data = request.json
    api_key = data.get('api_key')
    serial = data.get('serial')
    test_id = data.get('test_id')
    content = data.get('content')

    # Master API key bypass
    if api_key == MASTER_API_KEY:
        user = None  # Admin/master submission
    else:
        user = User.query.filter(User.api_keys.any()).all()
        user = next((u for u in user if u.check_api_key(api_key)), None)
        if not user:
            return jsonify({'error': 'Invalid API key'}), 403

    serialized_content = json.dumps(content)

    new_data = BatData(
        user_id=user.id if user else None,
        content=serialized_content,
        serial_number=serial,
        test_id=test_id
    )

    db.session.add(new_data)
    db.session.commit()
    return jsonify({'status': 'success'}), 200

@api_bp.route('/regenerate_api_key', methods=['POST'])
def regenerate_api_key():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to regenerate your API key.', 'danger')
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('app.login'))

    if not request.form.get('confirm'):
        flash('API key regeneration requires confirmation.', 'danger')
        return redirect(url_for('user_dashboard.user_dashboard'))

    new_api_key = secrets.token_hex(16)
    user.set_api_key(new_api_key)
    db.session.commit()
    session['api_key'] = new_api_key  # Store temporarily for display
    flash('API key regenerated successfully.', 'success')
    return redirect(url_for('user_dashboard.user_dashboard'))

