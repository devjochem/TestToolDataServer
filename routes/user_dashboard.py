import json
import secrets

from flask import Blueprint, session, redirect, url_for, request, render_template

from models import db, User, APIData, APIKey
from routes.base import login_required
from utils import get_serial_from_content

user_dashboard_bp = Blueprint("user_dashboard", __name__)

'''
        USER DASHBOARDS AND FUNCTIONS
'''

@user_dashboard_bp.route('/dashboard/serial/<serial>')
def serial_detail(serial):
    if session.get('admin'):
        all_data = APIData.query.all()
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('app.login'))
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

@user_dashboard_bp.route('/dashboard')
@login_required
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('app.login'))

    all_data = APIData.query.filter_by(user_id=user_id).all()

    serial_search = request.args.get('serial', '').strip()
    api_keys = user.api_keys

    serial_map = {}
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

    # sorted_serials = sorted(serial_map.items(), key=lambda x: x[0])
    sorted_serials = sorted(
        serial_map.items(),
        key=lambda x: max(entry['timestamp'] for entry in x[1]),
        reverse=True
    )

    '''for data_entry in user.api_data:
        try:
            content = json.loads(data_entry.content)
        except json.JSONDecodeError:
            continue
        if serial_search:
            serial = get_serial_from_content(content)
            if not serial or serial.lower() != serial_search.lower():
                continue
        data_entries.append({
            'timestamp': data_entry.timestamp,
            'content': content
        })'''

    return render_template('user_dashboard.html',serials=sorted_serials, api_keys=api_keys, api_key=session.get('api_key', 'Hidden for security'))


@user_dashboard_bp.route('/dashboard/settings')
@login_required
def user_settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('app.login'))

    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('app.login'))
    api_keys = user.api_keys

    return render_template('user_settings.html', api_keys=api_keys, api_key=session.get('api_key', 'Hidden for security'))


@user_dashboard_bp.route('/dashboard/all')
@login_required
def all_serials():
    if session.get('admin'):
        all_data = APIData.query.all()
    else:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('app.login'))
        all_data = APIData.query.filter_by(user_id=user_id).all()

    serial_map = {}
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

    # Get search query from URL
    search = request.args.get('search', '').strip().lower()

    # Filter serials if search is provided
    if search:
        serial_map = {s: v for s, v in serial_map.items() if search in s.lower()}

    advanced_search = request.args.get('search', '').strip().lower()
    #if advanced_search:


    # Sort serials by latest timestamp
    sorted_serials = sorted(
        serial_map.items(),
        key=lambda x: max(entry['timestamp'] for entry in x[1]),
        reverse=True
    )

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    total = len(sorted_serials)
    start = (page - 1) * per_page
    end = start + per_page
    serials_paginated = sorted_serials[start:end]
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'all_serials.html',
        serials=serials_paginated,
        page=page,
        total_pages=total_pages,
        search=search
    )

@user_dashboard_bp.route('/dashboard/api/delete/<int:key_id>', methods=['POST'])
@login_required
def delete_api_key(key_id):
    key = db.session.get(APIKey, key_id)
    if not key or key.user_id != session.get('user_id'):
        return redirect(url_for('user_dashboard.user_dashboard'))

    db.session.delete(key)
    db.session.commit()
    return redirect(url_for('user_dashboard.user_dashboard'))

@user_dashboard_bp.route('/dashboard/api/add', methods=['POST'])
@login_required
def add_api_key():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

    import secrets
    raw_key = secrets.token_hex(32)

    key_name = request.form.get("name")

    key = APIKey(user=user, name=key_name)
    key.set_key(raw_key)

    db.session.add(key)
    db.session.commit()

    return render_template("show_new_key.html", new_key=raw_key, key_name=key_name)